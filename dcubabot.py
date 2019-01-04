#!/usr/bin/python3
# -*- coding: utf-8 -*-

# STL imports
import sys
import logging
import datetime

# Non STL imports
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, Filters, CommandHandler, MessageHandler, CallbackQueryHandler)

# Local imports
# from tokenz import *
from models import *
from orga2Utils import noitip, asm

# TODO:Move this out of here
logging.basicConfig(
    level=logging.INFO,
    # level=logging.DEBUG,
    format='[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s',
    filename="bots.log")


# Globals ...... yes, globals
logger = logging.getLogger("DCUBABOT")


def start(bot, update):
    update.message.reply_text("Hola, ¿qué tal? ¡Mandame /help si no sabés qué puedo hacer!",
                              quote=False)


def help(bot, update):
    message_text = ""
    with db_session:
        for command in select(c for c in Command if c.description).order_by(lambda c: c.name):
            message_text += "/" + command.name + " - " + command.description + "\n"
    update.message.reply_text(message_text, quote=False)


def estasvivo(bot, update):
    update.message.reply_text("Sí, estoy vivo.", quote=False)


def list_buttons(bot, update, listable_type):
    with db_session:
        buttons = select(l for l in listable_type if l.validated).order_by(lambda l: l.name)
        keyboard = []
        columns = 3
        for k in range(0, len(buttons), columns):
            row = [InlineKeyboardButton(text=button.name, url=button.url,
                                        callback_data=button.url) for button in buttons[k:k + columns]]
            keyboard.append(row)
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text="Grupos: ", disable_web_page_preview=True,
                                  reply_markup=reply_markup, quote=False)


def listar(bot, update):
    list_buttons(bot, update, Obligatoria)


def listaroptativa(bot, update):
    list_buttons(bot, update, Optativa)


def listarotro(bot, update):
    list_buttons(bot, update, Otro)


def cubawiki(bot, update):
    with db_session:
        group = select(o for o in Obligatoria if o.chat_id == update.message.chat.id
                       and o.cubawiki_url is not None).first()
        if group:
            update.message.reply_text(group.cubawiki_url, quote=False)


def log_message(bot, update):
    user = str(update.message.from_user.id)
    # EAFP
    try:
        user_at_group = user+" @ " + update.message.chat.title
    except:
        user_at_group = user
    logger.info(user_at_group + ": " + update.message.text)


def felizdia_text(today):
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
             "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    dia = str(today.day)
    mes = int(today.month)
    mes = meses[mes - 1]
    return "Feliz " + dia + " de " + mes


def felizdia(bot, job):
    today = datetime.date.today()
    bot.send_message(chat_id="@dcfceynuba", text=felizdia_text(today))


def rozendioanalisis(bot, update):
    update.message.reply_text("No. Rozen todavia no dio el final de análisis.", quote=False)


def suggest_listable(bot, update, args, listable_type):
    try:
        name, url = " ".join(args).split("|")
    except:
        update.message.reply_text("Hiciste algo mal, la idea es que pongas:\n" +
                                  update.message.text.split()[0] + " <nombre>|<link>", quote=False)
        return
    with db_session:
        group = listable_type(name=name, url=url)
    keyboard = [
        [
            InlineKeyboardButton(text="Aceptar", callback_data=str(group.id) + '|1'),
            InlineKeyboardButton(text="Rechazar", callback_data=str(group.id) + '|0')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.sendMessage(chat_id=187622583, text="Obligatoria: " + name + "\n" + url,
                    reply_markup=reply_markup)
    update.message.reply_text("OK, se lo mando a Rozen.", quote=False)


def sugerirgrupo(bot, update, args):
    suggest_listable(bot, update, args, Obligatoria)


def sugeriroptativa(bot, update, args):
    suggest_listable(bot, update, args, Optativa)


def sugerirotro(bot, update, args):
    suggest_listable(bot, update, args, Otro)


def button(bot, update):
    query = update.callback_query
    message = query.message
    id, action = query.data.split("|")
    with db_session:
        group = Listable[int(id)]
        if action == "1":
            group.validated = True
            action_text = "\n¡Aceptado!"
        else:
            group.delete()
            action_text = "\n¡Rechazado!"
    bot.editMessageText(chat_id=message.chat_id, message_id=message.message_id,
                        text=message.text + action_text)


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
            (Filters.text | Filters.command), log_message), group=1)
        updater.job_queue.run_daily(callback=felizdia, time=datetime.time(second=3))
        init_db("dcubabot.sqlite3")
        with db_session:
            for command in select(c for c in Command):
                handler = CommandHandler(command.name, globals()[command.name],
                                         pass_args=command.args)
                dispatcher.add_handler(handler)
        dispatcher.add_handler(CallbackQueryHandler(button))
        # Start running the bot
        updater.start_polling(clean=True)
    except Exception as inst:
        logger.critical("ERROR AL INICIAR EL DCUBABOT")
        logger.exception(inst)


if __name__ == '__main__':
    from tokenz import *
    main()
