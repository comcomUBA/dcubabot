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
    Command(name="listaroptativa", description="Muestra todos los grupos de materias optativas conocidos por el bot")
    Command(name="listarotro", description="Muestra todos los grupos relacionados a la gente de este grupo "
                                           "(algo así como off-topics)")

    #TODO: Delete this
    Obligatoria.select().delete()
    Obligatoria(name="Sistemas", url="https://t.me/joinchat/CDIKsEAaiqgMpr47cW0I1Q", chat_id=-1)
    Obligatoria(name="Orga 1", url="https://t.me/joinchat/DS9ZukGbZgIOIaHgdBlavQ", chat_id=-1)
    Obligatoria(name="Orga 2", url="https://t.me/joinchat/Cy7kt0RKuAeYfsyffvTR2A", chat_id=-1)
    Obligatoria(name="Álgebra", url="https://t.me/algebra1dmuba", chat_id=-1)
    Optativa.select().delete()
    Optativa(name="PAP", url="https://telegram.me/PapDCUBA", chat_id=-1)
    Otro.select().delete()
    Otro(name="SPAM", url="https://t.me/joinchat/CDIKsEORDzVL5S2z2YwUQA", chat_id=-1)