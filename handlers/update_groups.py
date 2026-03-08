#!/usr/bin/python3
from time import sleep

from pony.orm import db_session, select
from telegram import Update
from telegram.ext import CallbackContext

from models import Listable
from tg_ids import DC_GROUP_CHATID


def update_group_url(
    context: CallbackContext,
    chat_id: str,
) -> tuple[str | None, str | None, bool]:
    try:
        url = context.bot.export_chat_invite_link(chat_id=chat_id)
    except Exception:  # TODO: filter excepts
        return None, None, False  # too GO-like huh?
    else:
        return chat_id, url, True  # too GO-like huh?


def update_groups(context: CallbackContext):
    with db_session:
        chats = list(
            select((item.id, item.chat_id, item.name) for item in Listable if item.validated),
        )
    for item_id, (_chat_id, url, validated), name in [
        (item_id, update_group_url(context, chat_id), name) for item_id, chat_id, name in chats
    ]:
        sleep(1)
        if not validated:
            with db_session:
                Listable[item_id].validated = False
            context.bot.send_message(
                chat_id=DC_GROUP_CHATID,
                text=f"El grupo {name} murió 💀",
            )
        else:
            with db_session:
                Listable[item_id].url = url


def actualizar_grupos(update: Update, context: CallbackContext):
    update_groups(context)
