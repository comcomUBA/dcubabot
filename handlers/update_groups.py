#!/usr/bin/python3
# -*- coding: utf-8 -*-
from time import sleep

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
    with db_session:
        chats = list(select((l.id, l.chat_id, l.name) for l in Listable if l.validated))
    for id, (chat_id, url, validated), name in [(id,update_group_url(context, chat_id), name) for id, chat_id, name in
                                                chats]:
        sleep(1)
        if not validated:
            with db_session:
                Listable[id].validated = False
            context.bot.send_message(chat_id="-1001067544716", text=f"El grupo {name} murió 💀")
        else:
            print(f"nuevo link de {name} es {url}")
            with db_session:
                Listable[id].url = url


def actualizar_grupos(update: Update, context: CallbackContext):
    update_groups(context)
