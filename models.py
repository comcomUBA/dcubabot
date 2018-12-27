#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pony.orm import *

db = Database()


class Command(db.Entity):
    name = Required(str)
    description = Optional(str)


db.bind('sqlite', 'commands.sqlite3', create_db=True)
db.generate_mapping(create_tables=True)
