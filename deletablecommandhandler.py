#!/usr/bin/python3
# -*- coding: utf-8 -*-

from telegram.ext import CommandHandler
from telegram.error import BadRequest
from models import *
import logging
logger = logging.getLogger("DCUBABOT")


class DeletableCommandHandler(CommandHandler):
    def _message_in_time_range(self, message):
        time_ellapsed = datetime.datetime.utcnow() - message.timestamp
        return time_ellapsed < datetime.timedelta(hours=24)

    def handle_update(self, update, dispatcher, check_result, context=None):
        #context.dispatcher = dispatcher
        context.sent_messages = []
        super().handle_update(update, dispatcher, check_result, context)

        with db_session:
            # Delete previous messages sent with the command in the group
            for message in select(m for m in SentMessage if
                                  m.command == self.command[0] and
                                  m.chat_id == update.effective_chat.id):
                if self._message_in_time_range(message):
                    try:
                        context.bot.delete_message(chat_id=message.chat_id,
                                                   message_id=message.message_id)
                    except BadRequest as e:
                        logger.info("Menssage already deleted, tabunn")
                    message.delete()

            # Insert new sent messages for later delete (only in groups)
            for message in context.sent_messages:
                if message.chat.type != "private":
                    SentMessage(command=self.command[0], chat_id=message.chat.id,
                                message_id=message.message_id)
