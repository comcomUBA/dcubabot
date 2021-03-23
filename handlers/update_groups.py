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
        chat_ids = select(l.id for l in Listable if l.validated)
    for chat_id, url, validated in [update_group_url(context, chat_id) for chat_id in chat_ids]:
        with db_session:
            if not validated:
                Listable[chat_id].validated = False
            else:
                Listable[chat_id].url = url


def actualizar_grupos(update: Update, context: CallbackContext):
    update_groups(context)
