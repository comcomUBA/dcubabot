#!/usr/bin/python3
from models import Obligatoria, db_session, init_db, select

init_db("dcubabot.sqlite3")

with db_session:
    buttons = select(item for item in Obligatoria if item.validated).order_by(
        lambda item: item.name,
    )
    print(list(buttons))
