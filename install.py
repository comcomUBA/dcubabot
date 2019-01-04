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
    Command(name="noitip", description="Escuchar un tip de noit de orga2")
    Command(name="asm", description="Información sobre una instrucción de Intel 64 o IA-32", args=True)
    Command(name="sugerirgrupo",
            description="Sugiere un grupo de alguna de las materias obligatorias", args=True)
    Command(name="sugeriroptativa",
            description="Sugiere un grupo de alguna de las materias optativas", args=True)
    Command(name="sugerirotro",
            description="Sugiere un grupo de cualquier cosa donde predomine gente de Exactas", args=True)
