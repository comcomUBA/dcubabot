#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pony.orm import *
from models import *

init_db("commands.sqlite3")
with db_session:
    Command.select().delete()
    Command(name="start")
    Command(name="help", description="Muestra este mensaje horrible")
    Command(name="estasvivo", description="Responde un mensaje corto para ver si el bot esta al día y activo")
    Command(name="listar", description="Muestra todos los grupos de materias obligatorias conocidos por el bot")

    Listable.select().delete()
    Listable(name="Sistemas", url="https://t.me/joinchat/CDIKsEAaiqgMpr47cW0I1Q")
    Listable(name="Orga 1", url="https://t.me/joinchat/DS9ZukGbZgIOIaHgdBlavQ")
    Listable(name="Orga 2", url="https://t.me/joinchat/Cy7kt0RKuAeYfsyffvTR2A")
    Listable(name="Álgebra", url="https://t.me/algebra1dmuba")