#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pony.orm import *
from models import *


def install_commands():
    with db_session:
        Command(name="start")
        Command(name="help", description="Muestra este mensaje horrible")
        Command(name="estasvivo",
                description="Responde un mensaje corto para ver si el bot esta al día y activo")
        Command(name="listar",
                description="Muestra todos los grupos de materias obligatorias conocidos por el bot")
        Command(name="listaroptativa",
                description="Muestra todos los grupos de materias optativas conocidos por el bot")
        Command(name="listarotro", description="Muestra todos los grupos relacionados a la gente de este grupo "
                                               "(algo así como off-topics)")
        Command(name="listarlabos", description="Lista las reservaciones de los laboratorios de la facultad")
        Command(name="cubawiki")
        Command(name="noitip", description="Escuchar un tip de noit de orga2")
        Command(name="asm", description="Información sobre una instrucción de Intel 64 o IA-32")
        Command(name="sugerirgrupo",
                description="Sugiere un grupo de alguna de las materias obligatorias")
        Command(name="sugeriroptativa",
                description="Sugiere un grupo de alguna de las materias optativas")
        Command(name="sugerirotro",
                description="Sugiere un grupo de cualquier cosa donde predomine gente de Exactas")
        Command(name="sugerirNoticia")
        # Administration commands
        Command(name="togglecommand")



if __name__ == '__main__':
    db.bind('sqlite', "dcubabot.sqlite3", create_db=True)
    db.drop_table("Command",if_exists=True, with_all_data=True)
    db.generate_mapping(create_tables=True)
    install_commands()
