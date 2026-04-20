#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.types import BigInteger

# --- Database Setup ---
Base = declarative_base()
engine = None
Session = None

def init_db():
    global engine, Session
    db_url = "cockroachdb://{user}:{password}@{host}:{port}/{database}".format(
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_URL"],
        port=os.environ["DB_PORT"],
        database="defaultdb"
    )
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

# --- Model Definitions ---

class Command(Base):
    __tablename__ = 'commands'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    enabled = Column(Boolean, nullable=False, default=True)

class SentMessage(Base):
    __tablename__ = 'sent_messages'
    id = Column(Integer, primary_key=True)
    command = Column(String, nullable=False)
    chat_id = Column(String, nullable=False)
    message_id = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

class Listable(Base):
    __tablename__ = 'listables'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    chat_id = Column(String)
    validated = Column(Boolean, default=False)
    type = Column(String(50))
    cubawiki_url = Column(String, nullable=True) # Specific to Obligatoria, null for others

    __mapper_args__ = {
        'polymorphic_identity': 'listable',
        'polymorphic_on': type
    }

class Obligatoria(Listable):
    __mapper_args__ = {
        'polymorphic_identity': 'Obligatoria',
    }

class Optativa(Listable):
    __mapper_args__ = {
        'polymorphic_identity': 'Optativa',
    }

class ECI(Listable):
    __mapper_args__ = {
        'polymorphic_identity': 'ECI',
    }

class Otro(Listable):
    __mapper_args__ = {
        'polymorphic_identity': 'Otro',
    }

class Grupo(Listable):
    __mapper_args__ = {
        'polymorphic_identity': 'Grupo',
    }

class GrupoOptativa(Listable):
    __mapper_args__ = {
        'polymorphic_identity': 'GrupoOptativa',
    }

class GrupoOtros(Listable):
    __mapper_args__ = {
        'polymorphic_identity': 'GrupoOtros',
    }

class Noticia(Base):
    __tablename__ = 'noticias'
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    date = Column(Date, nullable=False, default=datetime.date.today)
    validado = Column(Boolean, default=True)

class Noitip(Base):
    __tablename__ = 'noitips'
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)

class AsmInstruction(Base):
    __tablename__ = 'asm_instructions'
    id = Column(Integer, primary_key=True)
    mnemonic = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    url = Column(String, nullable=False)

class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False, unique=True)
    file_id = Column(String, nullable=False)
