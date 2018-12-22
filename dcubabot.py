#!/usr/bin/python3
# -*- coding: utf-8 -*-
# STL imports

import sys

# Non STL imports
from telegram.ext import (Updater, CommandHandler)

# Local imports
from tokenz import *

"""
start: Mensaje al mandar start que es la priemra vez q un usuario habla con el bot, o si alguien pone /start
"""


def start(bot, update):
    update.message.reply_text("Hola, ¿qué tal? ¡Mandame /help si no sabés qué puedo hacer!")


def help(bot, update):
    update.message.reply_text("Yo tampoco sé qué puedo hacer.")


def estasvivo(bot, update):
    update.message.reply_text("Sí, estoy vivo.")


def main():
    try:
        global update_id
        # Telegram Bot Authorization Token
        botname = "DCUBABOT"
        print("Iniciando DCUBABOT")
        updater = Updater(token=token)
        dispatcher = updater.dispatcher
        j = updater.job_queue

        commands = (line.rstrip('\n') for line in open('commands.txt'))
        for command in commands:
            handler = CommandHandler(command, globals()[command])
            dispatcher.add_handler(handler)

        # Start running the bot
        updater.start_polling(clean=True)
    except Exception as inst:
        print("ERROR AL INICIAR EL DCUBABOT")
        result = str(type(inst)) + "\n"		# the exception instancee
        result += str(inst.args) + "\n"	 # arguments stored in .args
        # __str__ allows args to be printed directly,
        result += str(inst) + "\n"
        print(result)


if __name__ == '__main__':
    main()
