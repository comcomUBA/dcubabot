#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pony.orm import *

db = Database()


class Command(db.Entity):
    name = Required(str)
    description = Optional(str)


class Listable(db.Entity):
    name = Required(str)
    url = Required(str)
    chat_id = Required(int, size=64)


class Obligatoria(Listable):
    cubawiki_url = Optional(str)


class Optativa(Listable):
    pass


class Otro(Listable):
    pass


def init_db(path):
    db.bind('sqlite', path, create_db=True)
    db.generate_mapping(create_tables=True)
