#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pony.orm import *
import datetime

db = Database()


class Command(db.Entity):
    name = Required(str)
    description = Optional(str)
    #enabled= Required(bool, default=True)


class SentMessage(db.Entity):
    command = Required(str)
    chat_id = Required(int, size=64)
    message_id = Required(int, size=64)
    timestamp = Required(datetime.datetime, default=datetime.datetime.utcnow)


class Listable(db.Entity):
    name = Required(str)
    url = Required(str)
    chat_id = Optional(int, size=64)
    validated = Required(bool, default=False)


class Obligatoria(Listable):
    cubawiki_url = Optional(str)


class Optativa(Listable):
    pass


class Otro(Listable):
    pass


class Noitip(db.Entity):
    text = Required(str)


class AsmInstruction(db.Entity):
    mnemonic = Required(str)
    summary = Required(str)
    url = Required(str)


def init_db(path):
    db.bind('sqlite', path, create_db=True)
    db.generate_mapping(create_tables=True)
