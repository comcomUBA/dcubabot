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
    with db_session:
        chats = select((l.id, l.name) for l in Listable if l.validated)
    for (chat_id, url, validated), name in [(update_group_url(context, chat_id), name) for chat_id, name in chats]:
        with db_session:
            if not validated:
                Listable[chat_id].validated = False
                chat_id = -1001067544716
                context.bot.send_message(chat_id=chat_id, text=f"El grupo {name} murió 💀")
            else:
                Listable[chat_id].url = url


def actualizar_grupos(update: Update, context: CallbackContext):
    update_groups(context)
