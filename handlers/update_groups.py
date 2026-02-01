#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
from time import sleep

from tg_ids import DC_GROUP_CHATID

from pony.orm import db_session, select
from telegram import Update
from telegram.ext import CallbackContext

from models import Listable

logger = logging.getLogger(__name__)


def update_group_url(context: CallbackContext, chat_id: str) -> (str, str, bool):
    try:
        url = context.bot.export_chat_invite_link(chat_id=chat_id)
        return chat_id, url, True  # too GO-like huh?
    except Exception:
        logger.error(f"Could not create invite link for {chat_id}", exc_info=True)
        return None, None, False  # too GO-like huh?


def update_groups(context: CallbackContext):
    logger.info("Starting update_groups job")
    with db_session:
        chats = list(select((l.id, l.chat_id, l.name) for l in Listable if l.validated))
    logger.info(f"Found {len(chats)} groups to update")

    for id, (chat_id, url, validated), name in [(id, update_group_url(context, chat_id), name) for id, chat_id, name in
                                                chats]:
        sleep(1)
        if not validated:
            logger.warning(f"Failed to update URL for group '{name}'. De-validating.")
            with db_session:
                Listable[id].validated = False
            context.bot.send_message(chat_id=DC_GROUP_CHATID, text=f"El grupo {name} murió 💀")
        else:
            logger.info(f"Updating URL for group '{name}'")
            with db_session:
                Listable[id].url = url
    logger.info("Finished update_groups job")


def actualizar_grupos(update: Update, context: CallbackContext):
    logger.info(f"Manual update of groups triggered by {update.effective_user.id}")
    update.message.reply_text("Actualizando grupos...")
    update_groups(context)
    update.message.reply_text("¡Grupos actualizados!")
