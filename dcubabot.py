#!/usr/bin/python3
# -*- coding: utf-8 -*-

# STL imports
import sys

# Non STL imports
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler)

# Local imports
from tokenz import *
from models import *

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
    keyboard_data = [
        [
            ["Texto 0", "https://url0.com", "data0"],
            ["Texto 1", "https://url1.com", "data1"],
            ["Texto 2", "https://url2.com", "data2"],
        ],
        [
            ["Texto 3", "https://url3.com", "data3"],
            ["Texto 4", "https://url4.com", "data4"],
            ["Texto 5", "https://url5.com", "data5"],
        ],
    ]
    keyboard = []
    for row in keyboard_data:
        keyboard.append(list(InlineKeyboardButton(
            text=button[0], url=button[1], callback_data=button[2]) for button in row))
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.sendMessage(update.message.chat_id, text="Grupos: ",
                    disable_web_page_preview=True, reply_markup=reply_markup)


def main():
    try:
        global update_id
        # Telegram Bot Authorization Token
        botname = "DCUBABOT"
        print("Iniciando DCUBABOT")
        updater = Updater(token=token)
        dispatcher = updater.dispatcher
        j = updater.job_queue

        with db_session:
            for command in select(c.name for c in Command):
                handler = CommandHandler(command, globals()[command])
                dispatcher.add_handler(handler)

        # Start running the bot
        updater.start_polling(clean=True)
    except Exception as inst:
        print("ERROR AL INICIAR EL DCUBABOT")
        result = str(type(inst)) + "\n"		# the exception instancee
        result += str(inst.args) + "\n"	 # arguments stored in .args
        result += str(inst) + "\n"
        print(result)


if __name__ == '__main__':
    main()
