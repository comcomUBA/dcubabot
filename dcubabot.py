#!/usr/bin/python3
# -*- coding: utf-8 -*-

# STL imports
import sys
import logging

# Non STL imports
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, Filters, CommandHandler, MessageHandler)

# Local imports
from tokenz import *
from models import *

# TODO:Move this out of here
logging.basicConfig(
    level=logging.INFO,
    # level=logging.DEBUG,
    format='[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s',
    filename="bots.log")


# Globals ...... yes, globals
logger = logging.getLogger("DCUBABOT")

"""
start: Mensaje al mandar start que es la priemra vez q un usuario habla con el bot, o si alguien pone /start
"""


def start(bot, update):
    update.message.reply_text("Hola, ¿qué tal? ¡Mandame /help si no sabés qué puedo hacer!")


def help(bot, update):
    message_text = ""
    with db_session:
        for command in select(c for c in Command if c.description).order_by(lambda c: c.name):
            message_text += "/" + command.name + " - " + command.description + "\n"
    update.message.reply_text(message_text)


def estasvivo(bot, update):
    update.message.reply_text("Sí, estoy vivo.")


# TODO: Rename
def list_buttons(bot, update, listable_type):
    with db_session:
        buttons = select(l for l in listable_type).order_by(lambda l: l.name)
        keyboard = []
        columns = 3
        for k in range(0, len(buttons), columns):
            row = [InlineKeyboardButton(text=button.name, url=button.url,
                                        callback_data=button.chat_id) for button in buttons[k:k + columns]]
            keyboard.append(row)
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.sendMessage(update.message.chat_id, text="Grupos: ",
                        disable_web_page_preview=True, reply_markup=reply_markup)


def listar(bot, update):
    list(bot, update, Obligatoria)


def listaroptativa(bot, update):
    list(bot, update, Optativa)


def listarotro(bot, update):
    list(bot, update, Otro)


def cubawiki(bot, update):
    with db_session:
        group = select(o for o in Obligatoria if o.chat_id == update.message.chat.id
                       and o.cubawiki_url is not None).first()
        if group:
            update.message.reply_text(group.cubawiki_url)


def messageLog(bot, update):
    user = str(update.message.from_user.id)
    # EAFP
    try:
        user_at_group = user+" @ " + update.message.chat.title
    except:
        user_at_group = user
    logger.info(user_at_group + ": " + update.message.text)


def main():
    try:
        global update_id
        # Telegram Bot Authorization Token
        botname = "DCUBABOT"
        print("Iniciando DCUBABOT")
        logger.info("Iniciando")
        updater = Updater(token=token)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(MessageHandler(
            (Filters.text | Filters.command), messageLog), group=1)
        init_db("dcubabot.sqlite3")
        with db_session:
            for command in select(c.name for c in Command):
                handler = CommandHandler(command, globals()[command])
                dispatcher.add_handler(handler)
        # Start running the bot
        updater.start_polling(clean=True)
    except Exception as inst:
        logger.critical("ERROR AL INICIAR EL DCUBABOT")
        logger.exception(inst)


if __name__ == '__main__':
    main()
