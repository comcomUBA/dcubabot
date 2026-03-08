#!/usr/bin/python3

import datetime
import logging
from typing import override

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CommandHandler

from context_types import DCUBACallbackContext
from models import SentMessage, db_session

logger = logging.getLogger("DCUBABOT")


class DeletableCommandHandler(CommandHandler):  # type: ignore[type-arg]
    def _message_in_time_range(self, message: SentMessage) -> bool:
        time_ellapsed = datetime.datetime.now(datetime.UTC) - message.timestamp
        return bool(time_ellapsed < datetime.timedelta(hours=24))

    @override
    async def handle_update(
        self,
        update: Update,
        application: object,
        check_result: object,
        context: DCUBACallbackContext,
    ) -> None:
        context.sent_messages = []
        await super().handle_update(update, application, check_result, context)  # type: ignore[arg-type]

        command_name = next(iter(self.commands))
        if update.effective_chat is None:
            return
        chat_id = update.effective_chat.id
        with db_session:
            # Delete previous messages sent with the command in the group
            # Filtro por command en DB; chat_id en Python (evita TO_BOOL con Pony+Py3.13)
            for message in list(SentMessage.select(lambda m: m.command == command_name)):
                if message.chat_id != chat_id:
                    continue
                if self._message_in_time_range(message):
                    try:
                        await context.bot.delete_message(
                            chat_id=message.chat_id,
                            message_id=message.message_id,
                        )
                    except BadRequest:
                        logger.info("Menssage already deleted, tabunn")
                    message.delete()

            # Insert new sent messages for later delete (only in groups)
            for message in context.sent_messages:
                if message.chat.type != "private":
                    SentMessage(
                        command=command_name,
                        chat_id=message.chat.id,
                        message_id=message.message_id,
                    )
