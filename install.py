#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pony.orm import *
from models import *

init_db("dcubabot.sqlite3")
with db_session:
    Command.select().delete()
    Command(name="start")
    Command(name="help", description="Muestra este mensaje horrible")
    Command(name="estasvivo", description="Responde un mensaje corto para ver si el bot esta al día y activo")
    Command(name="listar", description="Muestra todos los grupos de materias obligatorias conocidos por el bot")
    Command(name="listaroptativa",
            description="Muestra todos los grupos de materias optativas conocidos por el bot")
    Command(name="listarotro", description="Muestra todos los grupos relacionados a la gente de este grupo "
                                           "(algo así como off-topics)")
    Command(name="cubawiki")
    Command(name="rozendioanalisis", description="Te dice si Rozen ya dio el final de análisis o no")
    Command(name="noitip")
    Command(name="asm", args=True)
