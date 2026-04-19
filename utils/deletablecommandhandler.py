#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
from telegram.ext import CommandHandler
from telegram.error import BadRequest
from models import Session, SentMessage
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

        session = Session()
        try:
            # Delete previous messages sent with the command in the group
            messages_to_delete = session.query(SentMessage).filter_by(
                command=self.command[0],
                chat_id=update.effective_chat.id
            ).all()

            for message in messages_to_delete:
                if self._message_in_time_range(message):
                    try:
                        context.bot.delete_message(chat_id=message.chat_id,
                                                   message_id=message.message_id)
                    except BadRequest as e:
                        logger.info("Message already deleted, tabunn")
                    session.delete(message)

            # Insert new sent messages for later delete (only in groups)
            for message in context.sent_messages:
                if message.chat.type != "private":
                    new_message = SentMessage(
                        command=self.command[0],
                        chat_id=message.chat.id,
                        message_id=message.message_id,
                        timestamp=datetime.datetime.utcnow()
                    )
                    session.add(new_message)
            
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error in DeletableCommandHandler: {e}")
        finally:
            session.close()
