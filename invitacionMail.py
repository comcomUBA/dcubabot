#!/usr/bin/python3
# -*- coding: utf-8 -*-
from models import *
init_db("dcubabot.sqlite3")

with db_session:
    buttons = select(l for l in Obligatoria if l.validated).order_by(lambda l: l.name)
    print(list(buttons))
