#!/usr/bin/python3
# -*- coding: utf-8 -*-
from pony.orm import db_session, select
from telegram import Update
from telegram.ext import Updater, CallbackContext

from models import Listable


def update_group_url(context: CallbackContext, chat_id: str) -> (str, str, bool):
    try:
        url = context.bot.export_chat_invite_link(chat_id=chat_id)
        return chat_id, url, True  # too GO-like huh?
    except:  # TODO: filter excepts
        return None, None, False  # too GO-like huh?


def update_groups(context: CallbackContext):
    print("voy a actualizar grupos")
    with db_session:
        chats = list(select((l.id, l.name) for l in Listable if l.validated))
    print(f"voy a actualizar {chats}")
    for (chat_id, url, validated), name in [(update_group_url(context, chat_id), name) for chat_id, name in chats]:
        print(f"lo que va pasar es que {((chat_id, url, validated), name)} ")
        if not validated:
            with db_session:
                print("mira q lo borro")
                Listable[chat_id].validated = False
                print("lo borre")
            print("mira q lo mando")
            context.bot.send_message(chat_id="-1001067544716", text=f"El grupo {name} murió 💀")
            print("lo mandé")
        else:
            with db_session:
                Listable[chat_id].url = url


def actualizar_grupos(update: Update, context: CallbackContext):
    update_groups(context)
