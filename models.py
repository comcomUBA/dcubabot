#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pony.orm import *

db = Database()


class Command(db.Entity):
    name = Required(str)
    description = Optional(str)
    args = Required(bool, default=False)


class Listable(db.Entity):
    name = Required(str)
    url = Required(str)
    chat_id = Optional(int, size=64)


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
