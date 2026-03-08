#!/usr/bin/python3
from models import Obligatoria, db_session, init_db

init_db("dcubabot.sqlite3")

with db_session:
    buttons = list(Obligatoria.select(lambda item: item.validated).order_by(lambda item: item.name))
    print(list(buttons))
