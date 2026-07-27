#!/usr/bin/env python3
import os
import unittest
import datetime
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Mock environmental variables for db (not used by SQLite but needed by code initialization imports)
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_URL", "localhost")
os.environ.setdefault("DB_PORT", "26257")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "1234:test_token")

import models
from models import Base, Listable, GrupoOptativa, ECI, Grupo, GrupoArchivado

class TestGroupArchiving(unittest.TestCase):
    def setUp(self):
        # Set up an in-memory SQLite database for testing the logic
        self.engine = create_engine("sqlite:///:memory:")
        models.engine = self.engine
        models.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.Session = models.Session

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_database_columns_and_subclass_exist(self):
        # Verify the new columns exist on the Listable model
        self.assertTrue(hasattr(Listable, "last_activity"))
        self.assertTrue(hasattr(Listable, "warned_at"))
        self.assertTrue(hasattr(Listable, "archived_at"))
        # Verify the GrupoArchivado subclass is defined
        self.assertTrue(issubclass(GrupoArchivado, Listable))

    def test_default_values(self):
        session = self.Session()
        group = GrupoOptativa(name="Test Optativa", url="https://t.me/test_opt")
        session.add(group)
        session.commit()

        # Check default values are correct
        retrieved = session.query(GrupoOptativa).first()
        self.assertEqual(retrieved.type, "GrupoOptativa")
        self.assertIsNotNone(retrieved.last_activity)
        self.assertIsNone(retrieved.warned_at)
        self.assertIsNone(retrieved.archived_at)
        session.close()

    def test_filtering_active_and_archived_groups(self):
        session = self.Session()
        
        # Create active and archived groups
        active_opt = GrupoOptativa(name="Active Optativa", url="https://t.me/active_opt", validated=True)
        archived_opt = GrupoArchivado(name="Archived Optativa", url="https://t.me/archived_opt", validated=True, archived_at=datetime.datetime.utcnow())
        active_eci = ECI(name="Active ECI", url="https://t.me/active_eci", validated=True)
        archived_eci = GrupoArchivado(name="Archived ECI", url="https://t.me/archived_eci", validated=True, archived_at=datetime.datetime.utcnow())
        
        session.add_all([active_opt, archived_opt, active_eci, archived_eci])
        session.commit()

        # Query active optativas (similar to listaroptativa)
        # It automatically excludes GrupoArchivado!
        active_optativas = session.query(GrupoOptativa).filter_by(validated=True).all()
        self.assertEqual(len(active_optativas), 1)
        self.assertEqual(active_optativas[0].name, "Active Optativa")

        # Query active ECIs (similar to listareci)
        active_ecis = session.query(ECI).filter_by(validated=True).all()
        self.assertEqual(len(active_ecis), 1)
        self.assertEqual(active_ecis[0].name, "Active ECI")

        # Query archived groups of ECI and GrupoOptativa (similar to listararchivado)
        archived_groups = session.query(GrupoArchivado).filter_by(validated=True).all()
        self.assertEqual(len(archived_groups), 2)
        archived_names = [g.name for g in archived_groups]
        self.assertIn("Archived Optativa", archived_names)
        self.assertIn("Archived ECI", archived_names)
        
        session.close()

    def test_auto_archiving_logic(self):
        session = self.Session()
        
        now = datetime.datetime.utcnow()
        threshold_warn_date = now - datetime.timedelta(days=365) # More than 364 days ago
        six_months_ago = now - datetime.timedelta(days=180) # Active group

        old_opt = GrupoOptativa(name="Old Opt", url="url1", chat_id="123", validated=True, last_activity=threshold_warn_date, warned_at=None)
        recent_opt = GrupoOptativa(name="Recent Opt", url="url2", chat_id="456", validated=True, last_activity=six_months_ago, warned_at=None)
        old_eci = ECI(name="Old ECI", url="url3", chat_id="789", validated=True, last_activity=threshold_warn_date, warned_at=None)
        old_regular_group = Grupo(name="Old Regular Group", url="url4", chat_id="1011", validated=True, last_activity=threshold_warn_date, warned_at=None)
        warned_opt = GrupoOptativa(name="Warned Opt", url="url5", chat_id="1213", validated=True, last_activity=threshold_warn_date, warned_at=now - datetime.timedelta(hours=25)) # Warned > 24h ago

        session.add_all([old_opt, recent_opt, old_eci, old_regular_group, warned_opt])
        session.commit()

        # Simulate update_groups automatic archiving logic with warning support
        threshold_warn = now - datetime.timedelta(days=364)
        
        # 1. Initialize None last_activities
        untracked = session.query(Listable).filter(Listable.last_activity == None).all()
        for g in untracked:
            g.last_activity = now
            
        # 2. Process candidates (validated and active ECI and GrupoOptativa)
        # Their type is 'GrupoOptativa' or 'ECI' (i.e. not 'GrupoArchivado')
        candidates = session.query(Listable).filter(
            Listable.type.in_(["GrupoOptativa", "ECI"]),
            Listable.validated == True
        ).all()
        
        for g in candidates:
            # Case 1: Inactive and not warned
            if g.last_activity < threshold_warn and g.warned_at is None:
                g.warned_at = now
            # Case 2: Warned and 24 hours have passed
            elif g.warned_at is not None and (now - g.warned_at) >= datetime.timedelta(hours=24):
                g.type = "GrupoArchivado"
                g.warned_at = None
                g.archived_at = now
                
        session.commit()

        # Verify results
        # Old Opt should now have warned_at set (Case 1)
        self.assertIsNotNone(session.query(GrupoOptativa).filter_by(name="Old Opt").one().warned_at)
        self.assertEqual(session.query(GrupoOptativa).filter_by(name="Old Opt").one().type, "GrupoOptativa")

        # Recent Opt should remain active and NOT warned
        self.assertIsNotNone(session.query(GrupoOptativa).filter_by(name="Recent Opt").first())
        self.assertIsNone(session.query(GrupoOptativa).filter_by(name="Recent Opt").one().warned_at)

        # Old ECI should now have warned_at set (Case 1)
        self.assertIsNotNone(session.query(ECI).filter_by(name="Old ECI").one().warned_at)

        # Old Regular Group (type Grupo) should NOT be warned or archived
        self.assertIsNotNone(session.query(Grupo).filter_by(name="Old Regular Group").first())
        self.assertIsNone(session.query(Grupo).filter_by(name="Old Regular Group").one().warned_at)

        # Warned Opt (which was warned 25h ago) should now be archived (Case 2)
        # Meaning its type is now GrupoArchivado and it is not found as GrupoOptativa
        self.assertIsNone(session.query(GrupoOptativa).filter_by(name="Warned Opt").first())
        self.assertIsNotNone(session.query(GrupoArchivado).filter_by(name="Warned Opt").first())
        self.assertIsNone(session.query(GrupoArchivado).filter_by(name="Warned Opt").one().warned_at)
        self.assertIsNotNone(session.query(GrupoArchivado).filter_by(name="Warned Opt").one().archived_at)
        
        session.close()

    def test_track_activity_behavior(self):
        session = self.Session()
        
        # 1. Create a healthy group
        healthy = GrupoOptativa(name="Healthy Opt", url="url1", chat_id="999", validated=True, last_activity=datetime.datetime.utcnow() - datetime.timedelta(days=10), warned_at=None)
        # 2. Create a warned group
        warned_time = datetime.datetime.utcnow() - datetime.timedelta(hours=2)
        warned = GrupoOptativa(name="Warned Opt", url="url2", chat_id="888", validated=True, last_activity=datetime.datetime.utcnow() - datetime.timedelta(days=365), warned_at=warned_time)
        
        session.add_all([healthy, warned])
        session.commit()
        
        # Define the track_activity logic simulation
        def simulate_track_activity(chat_id):
            with self.Session() as s:
                group = s.query(Listable).filter_by(chat_id=str(chat_id)).first()
                if group and group.warned_at is None:
                    group.last_activity = datetime.datetime.utcnow()
                s.commit()
                
        # Simulate normal activity in healthy group (id 999) -> SHOULD update activity
        simulate_track_activity(999)
        
        # Verify healthy group updated its activity
        healthy_retrieved = session.query(GrupoOptativa).filter_by(chat_id="999").one()
        self.assertGreater(healthy_retrieved.last_activity, datetime.datetime.utcnow() - datetime.timedelta(minutes=1))
        
        # Simulate normal activity in warned group (id 888) -> SHOULD NOT update activity or clear warned_at
        simulate_track_activity(888)
        
        # Verify warned group did NOT update activity and still has warned_at set
        warned_retrieved = session.query(GrupoOptativa).filter_by(chat_id="888").one()
        self.assertLess(warned_retrieved.last_activity, datetime.datetime.utcnow() - datetime.timedelta(days=100))
        self.assertEqual(warned_retrieved.warned_at, warned_time)
        session.close()

if __name__ == "__main__":
    unittest.main()
