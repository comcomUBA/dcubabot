#!/usr/bin/python3
# -*- coding: utf-8 -*-

# STL imports
import sys
import logging

# Non STL imports
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler)

# Local imports
from tokenz import *
from models import *

# TODO:Move this from here
logging.basicConfig(
    level=logging.INFO,
    # level=logging.DEBUG,
    format='[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s',
    filename="bots.log")


# Globals ...... yes, globals
logger = logging.getLogger("Bots.log")

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


def listar(bot, update):
    with db_session:
        buttons = select(l for l in Listable).order_by(lambda l: l.name)
        keyboard = []
        columns = 3
        for k in range(0, len(buttons), columns):
            keyboard.append(list(InlineKeyboardButton(
                text=button.name, url=button.url, callback_data=button.url) for button in buttons[k:k+columns]))
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.sendMessage(update.message.chat_id, text="Grupos: ",
                        disable_web_page_preview=True, reply_markup=reply_markup)


def main():
    try:
        global update_id
        # Telegram Bot Authorization Token
        botname = "DCUBABOT"
        print("Iniciando DCUBABOT")
        logger.info("Iniciando DCUBABOT")
        updater = Updater(token=token)
        dispatcher = updater.dispatcher

        init_db("commands.sqlite3")
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
