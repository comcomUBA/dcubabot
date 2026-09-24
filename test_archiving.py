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

    def test_24h_warning_and_auto_archiving_logic(self):
        session = self.Session()
        now = datetime.datetime.utcnow()

        # 1. Group active within last year -> no action
        group_recent = GrupoOptativa(name="Recent Group", url="https://t.me/recent", chat_id="111", validated=True, last_activity=now - datetime.timedelta(days=100))
        
        # 2. Group inactive > 1 year, warned_at is None -> needs warning
        group_inactive_no_warning = GrupoOptativa(name="Inactive No Warn", url="https://t.me/nowarn", chat_id="222", validated=True, last_activity=now - datetime.timedelta(days=366))
        
        # 3. Group warned < 24h ago -> wait, no archive yet
        group_warned_recent = GrupoOptativa(name="Warned Recent", url="https://t.me/warn_rec", chat_id="333", validated=True, last_activity=now - datetime.timedelta(days=366), warned_at=now - datetime.timedelta(hours=10))
        
        # 4. Group warned >= 24h ago -> auto-archive now!
        group_warned_old = GrupoOptativa(name="Warned Old", url="https://t.me/warn_old", chat_id="444", validated=True, last_activity=now - datetime.timedelta(days=366), warned_at=now - datetime.timedelta(hours=25))

        session.add_all([group_recent, group_inactive_no_warning, group_warned_recent, group_warned_old])
        session.commit()

        # Simulate update_groups archiving logic
        threshold_warn = now - datetime.timedelta(days=364)
        candidates = session.query(Listable).filter_by(validated=True).all()
        
        for group in candidates:
            if not group.es_archivable:
                continue
            if group.last_activity < threshold_warn and group.warned_at is None:
                group.warned_at = now
            elif group.warned_at is not None and (now - group.warned_at) >= datetime.timedelta(hours=24):
                group.type = "GrupoArchivado"
                group.warned_at = None
                group.archived_at = now

        session.commit()

        # Verify results
        g1 = session.query(Listable).filter_by(chat_id="111").first()
        self.assertEqual(g1.type, "GrupoOptativa")
        self.assertIsNone(g1.warned_at)

        g2 = session.query(Listable).filter_by(chat_id="222").first()
        self.assertEqual(g2.type, "GrupoOptativa")
        self.assertIsNotNone(g2.warned_at)

        g3 = session.query(Listable).filter_by(chat_id="333").first()
        self.assertEqual(g3.type, "GrupoOptativa")
        self.assertIsNotNone(g3.warned_at)

        g4 = session.query(Listable).filter_by(chat_id="444").first()
        self.assertEqual(g4.type, "GrupoArchivado")
        self.assertIsNone(g4.warned_at)
        self.assertIsNotNone(g4.archived_at)

        session.close()

    def test_unarchiving_on_readdition(self):
        # Test unarchiving logic when re-adding an archived group via agregar
        session = self.Session()
        archived_opt = GrupoArchivado(
            name="Archived Optativa",
            url="https://t.me/old_link",
            chat_id="555",
            validated=True,
            archived_at=datetime.datetime.utcnow() - datetime.timedelta(days=10)
        )
        session.add(archived_opt)
        session.commit()
        session.close()

        # Execute unarchiving logic using polymorphic reactivar
        session = self.Session()
        group = session.query(Listable).filter_by(chat_id="555").first()
        self.assertEqual(group.type, "GrupoArchivado")

        action = group.reactivar(session, "https://t.me/new_link", "Re-added Optativa", GrupoOptativa)
        session.commit()
        self.assertEqual(action, Listable.REACTIVAR_ARCHIVED)

        retrieved = session.query(Listable).filter_by(chat_id="555").first()
        self.assertEqual(retrieved.type, "GrupoOptativa")
        self.assertEqual(retrieved.name, "Re-added Optativa")
        self.assertEqual(retrieved.url, "https://t.me/new_link")
        self.assertIsNone(retrieved.archived_at)
        self.assertIsNone(retrieved.warned_at)
        self.assertTrue(retrieved.validated)
        session.close()

    def test_middleware_activity_tracking(self):
        session = self.Session()
        now = datetime.datetime.utcnow()
        healthy = GrupoOptativa(name="Healthy Opt", url="url1", chat_id="999", validated=True, last_activity=now - datetime.timedelta(days=10), warned_at=None)
        warned_time = now - datetime.timedelta(hours=2)
        warned = GrupoOptativa(name="Warned Opt", url="url2", chat_id="888", validated=True, last_activity=now - datetime.timedelta(days=365), warned_at=warned_time)
        session.add_all([healthy, warned])
        session.commit()

        # Simulate message received in group 999
        g = session.query(Listable).filter_by(chat_id="999").first()
        g.last_activity = datetime.datetime.utcnow()
        session.commit()

        # Simulate message received in group 888 (warned group)
        g_warned = session.query(Listable).filter_by(chat_id="888").first()
        g_warned.last_activity = datetime.datetime.utcnow()
        g_warned.warned_at = None
        session.commit()

        healthy_retrieved = session.query(Listable).filter_by(chat_id="999").first()
        self.assertGreater(healthy_retrieved.last_activity, now - datetime.timedelta(minutes=1))

        warned_retrieved = session.query(Listable).filter_by(chat_id="888").first()
        self.assertIsNone(warned_retrieved.warned_at)
        self.assertGreater(warned_retrieved.last_activity, now - datetime.timedelta(minutes=1))

        session.close()

    def test_reactivation_of_warned_group_on_agregar(self):
        session = self.Session()
        now = datetime.datetime.utcnow()
        warned_time = now - datetime.timedelta(hours=12)
        warned = GrupoOptativa(name="Warned Group", url="https://t.me/warned", chat_id="999", validated=True, last_activity=now - datetime.timedelta(days=365), warned_at=warned_time)
        session.add(warned)
        session.commit()
        session.close()

        import asyncio
        async def run_test():
            update = AsyncMock()
            update.effective_chat = MagicMock()
            update.effective_chat.id = 999
            update.effective_chat.title = "Updated Title"
            update.effective_message = AsyncMock()
            
            context = AsyncMock()
            context.bot = AsyncMock()
            context.bot.export_chat_invite_link = AsyncMock(return_value="https://t.me/new_warned_link")
            
            from handlers.groups import agregar
            await agregar(update, context, GrupoOptativa, "optativa")
            
            session2 = self.Session()
            group = session2.query(Listable).filter_by(chat_id="999").first()
            self.assertEqual(group.type, "GrupoOptativa")
            self.assertEqual(group.name, "Updated Title")
            self.assertEqual(group.url, "https://t.me/new_warned_link")
            self.assertIsNone(group.warned_at)
            session2.close()
            
            update.effective_message.reply_text.assert_called_with(
                text="¡El grupo ha sido reactivado y se ha cancelado el aviso de archivado!"
            )
        asyncio.run(run_test())

    def test_reactivation_of_unvalidated_group_on_agregar(self):
        session = self.Session()
        now = datetime.datetime.utcnow()
        unvalidated = GrupoOptativa(name="Unvalidated Group", url="https://t.me/unval", chat_id="111", validated=False, last_activity=now)
        session.add(unvalidated)
        session.commit()
        session.close()

        import asyncio
        async def run_test():
            update = AsyncMock()
            update.effective_chat = MagicMock()
            update.effective_chat.id = 111
            update.effective_chat.title = "Updated Unvalidated Title"
            update.effective_message = AsyncMock()
            
            context = AsyncMock()
            context.bot = AsyncMock()
            context.bot.export_chat_invite_link = AsyncMock(return_value="https://t.me/new_unval_link")
            context.bot.send_message = AsyncMock()
            
            from handlers.groups import agregar
            await agregar(update, context, GrupoOptativa, "optativa")
            
            session2 = self.Session()
            group = session2.query(Listable).filter_by(chat_id="111").first()
            self.assertEqual(group.type, "GrupoOptativa")
            self.assertEqual(group.name, "Updated Unvalidated Title")
            self.assertEqual(group.url, "https://t.me/new_unval_link")
            self.assertFalse(group.validated)
            session2.close()
            
            context.bot.send_message.assert_called_once()
            call_kwargs = context.bot.send_message.call_args[1]
            self.assertIn("optativa (re-enviado para validación)", call_kwargs["text"])
            
            update.effective_message.reply_text.assert_called_with(
                "OK, el grupo no estaba validado o fue desactivado. Se lo vuelvo a mandar a Rozen para su aprobación."
            )
        asyncio.run(run_test())

    def test_polymorphic_properties(self):
        from models import GrupoOptativa, ECI, Grupo, GrupoOtros
        
        opt = GrupoOptativa(name="Opt", url="url")
        eci = ECI(name="ECI", url="url")
        group = Grupo(name="Grupo", url="url")
        otros = GrupoOtros(name="Otros", url="url")
        
        # Test es_archivable
        self.assertTrue(opt.es_archivable)
        self.assertTrue(eci.es_archivable)
        self.assertFalse(group.es_archivable)
        self.assertFalse(otros.es_archivable)
        
        # Test comando_agregar
        self.assertEqual(opt.comando_agregar, "agregaroptativa")
        self.assertEqual(eci.comando_agregar, "agregareci")
        self.assertEqual(group.comando_agregar, "agregargrupo")
        self.assertEqual(otros.comando_agregar, "agregarotros")

    def test_safe_reply_deleted_message_fallback(self):
        import asyncio
        from telegram.error import BadRequest
        from handlers.groups import safe_reply

        async def run_test():
            update = AsyncMock()
            update.effective_chat = MagicMock()
            update.effective_chat.id = 12345
            update.effective_message = AsyncMock()
            update.effective_message.reply_text.side_effect = BadRequest("Message to be replied not found")

            context = AsyncMock()
            context.bot = AsyncMock()

            await safe_reply(update, context, text="Grupos: ")

            # Should fall back to context.bot.send_message with chat_id
            context.bot.send_message.assert_called_once_with(
                chat_id=12345,
                text="Grupos: "
            )

        asyncio.run(run_test())

    def test_list_buttons_handles_deleted_message(self):
        import asyncio
        from telegram.error import BadRequest
        from handlers.groups import list_buttons
        from models import Grupo

        session = self.Session()
        session.add(Grupo(name="Algo1", url="https://t.me/algo1", validated=True))
        session.commit()
        session.close()

        async def run_test():
            update = AsyncMock()
            update.effective_chat = MagicMock()
            update.effective_chat.id = 12345
            update.effective_message = AsyncMock()
            update.effective_message.reply_text.side_effect = BadRequest("Message to be replied not found")

            context = AsyncMock()
            context.bot = AsyncMock()

            await list_buttons(update, context, Grupo)

            context.bot.send_message.assert_called_once()
            call_kwargs = context.bot.send_message.call_args[1]
            self.assertEqual(call_kwargs["chat_id"], 12345)
            self.assertEqual(call_kwargs["text"], "Grupos: ")

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()