#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pony.orm import *
from models import *


@db_session
def check_or_install_command(**kwargs):
    try:
        if not Command.get(name=kwargs["name"]):
            print(Command(**kwargs))

    except Exception as e:
        print("elol", e)


def install_check_or_install_commands():

    with db_session:

        check_or_install_command(name="start")
        check_or_install_command(
            name="help",
            description="Muestra este mensaje horrible")

        check_or_install_command(
            name="estasvivo",
            description="Responde un mensaje corto para ver si el bot "
                        "esta al día y activo")

        check_or_install_command(
            name="listar",
            description="Muestra todos los grupos de materias obligatorias "
                        "conocidos por el bot")

        check_or_install_command(
            name="listaroptativa",
            description="Muestra todos los grupos de materias optativas "
                        "conocidos por el bot")

        check_or_install_command(
            name="listareci",
            description="Muestra todos los grupos de cursos de la ECI")

        check_or_install_command(
            name="listarotro",
            description="Muestra todos los grupos relacionados a la gente de este grupo "
                        "(algo así como off-topics)")

        check_or_install_command(
            name="listarlabos",
            description="Lista las reservaciones de los laboratorios de la facultad")

        check_or_install_command(name="cubawiki")

        check_or_install_command(
            name="noitip",
            description="Escuchar un tip de noit de orga2")

        check_or_install_command(
            name="asm",
            description="Información sobre una instrucción de Intel 64 o IA-32")

        check_or_install_command(
            name="sugerirgrupo",
            description="Sugiere un grupo de alguna de las materias obligatorias")

        check_or_install_command(
            name="sugeriroptativa",
            description="Sugiere un grupo de alguna de las materias optativas")

        check_or_install_command(
            name="sugerireci",
            description="Sugiere un grupo de alguno de los cursos de la ECI")

        check_or_install_command(
            name="sugerirotro",
            description="Sugiere un grupo de cualquier cosa "
                        "donde predomine gente de Exactas")

        check_or_install_command(
            name="flan",
            description="Muestra el grafo de materias de la carrera "
                        "con correlatividades")

        check_or_install_command(name="sugerir")

        check_or_install_command(name="sugerirNoticia")
        check_or_install_command(
            name="checodepers", 
            desciption="Envia un mensaje con tus consultas a los codepers" 
                       "para que ellos se pongan en contacto con vos"
          )

        # Administration commands
        check_or_install_command(name="togglecommand")


if __name__ == '__main__':
    db.bind('sqlite', "dcubabot.sqlite3", create_db=True)
    # db.drop_table("Command",if_exists=True, with_all_data=True)
    db.generate_mapping(create_tables=True)
    install_check_or_install_commands()
