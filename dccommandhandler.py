#!/usr/bin/python3
# -*- coding: utf-8 -*-

from telegram.ext import CommandHandler
from models import *


class DCCommandHandler(CommandHandler):

    def handle_update(self, update, dispatcher, check_result, context=None):
        with db_session:
            command_enabled = Command.get(name=self.command[0]).enabled

        if command_enabled:
            context.dc_sent_messages = []
            super().handle_update(update, dispatcher, check_result, context)

            with db_session:
                # Delete previous messages sent with the command in the group
                for message in select(m for m in SentMessage
                                          if m.command == self.command[0]):
                    if datetime.datetime.utcnow() - message.timestamp < datetime.timedelta(hours=24):
                        context.bot.delete_message(chat_id=message.chat_id,
                                                   message_id=message.message_id)
                    message.delete()

                # Insert new sent messages for later delete (only in groups)
                for message in context.dc_sent_messages:
                    if message.chat.type != "private":
                        SentMessage(command=self.command[0], chat_id=message.chat.id,
                                    message_id=message.message_id)
