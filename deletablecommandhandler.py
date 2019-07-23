#!/usr/bin/python3
# -*- coding: utf-8 -*-

from telegram.ext import CommandHandler
from models import *


class DeletableCommandHandler(CommandHandler):

    def handle_update(self, update, dispatcher, check_result, context=None):
        context.dispatcher = dispatcher
        context.sent_messages = []
        super().handle_update(update, dispatcher, check_result, context)

        with db_session:
            # Delete previous messages sent with the command in the group
            for message in select(m for m in SentMessage
                                  if m.command == self.command[0]
                                  and m.chat_id == update.effective_chat.id):
                if datetime.datetime.utcnow() - message.timestamp < datetime.timedelta(hours=24):
                    context.bot.delete_message(chat_id=message.chat_id,
                                               message_id=message.message_id)
                message.delete()

            # Insert new sent messages for later delete (only in groups)
            for message in context.sent_messages:
                if message.chat.type != "private":
                    SentMessage(command=self.command[0], chat_id=message.chat.id,
                                message_id=message.message_id)
