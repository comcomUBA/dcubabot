#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pony.orm import *
from models import *

with db_session:
    init_db("commands.sqlite3")
    Command.select().delete()
    Command(name="start")
    Command(name="help", description="Muestra este mensaje horrible")
    Command(name="estasvivo", description="Responde un mensaje corto para ver si el bot esta al día y activo")
    Command(name="listar", description="Muestra todos los grupos de materias obligatorias conocidos por el bot")
