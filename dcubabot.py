#!/usr/bin/python3
# -*- coding: utf-8 -*-

# STL imports
import sys
import logging
import datetime

# Non STL imports
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, Filters, CommandHandler, MessageHandler)

# Local imports
# from tokenz import *
from models import *

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
        buttons = select(l for l in listable_type).order_by(lambda l: l.name)
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


def noitip(bot, update):
    with db_session:
        random_noitip = Noitip.select_random(1)[0].text
    update.message.reply_text(random_noitip, quote=False)


def asm(bot, update, args):
    if not args:
        update.message.reply_text("No me pasaste ninguna instrucción.", quote=False)
        return

    mnemonic = args[0].upper()
    with db_session:
        possibles = [i for i in list(AsmInstruction.select())
                     if levenshtein(mnemonic, i.mnemonic) < 2]
    if not possibles:
        update.message.reply_text("No pude encontrar esa instrucción.", quote=False)
    elif mnemonic == possibles[0].mnemonic:
        update.message.reply_text(getasminfo(possibles[0]), quote=False)
    else:
        response_text = ("No pude encontrar esa instrucción.\n"
                         "Quizás quisiste decir:")
        for instr in possibles:
            response_text += "\n" + getasminfo(instr)
        update.message.reply_text(response_text, quote=False)


def levenshtein(string1, string2):
    len1 = len(string1) + 1
    len2 = len(string2) + 1

    tbl = {}
    for i in range(len1):
        tbl[i, 0] = i
    for j in range(len2):
        tbl[0, j] = j
    for i in range(1, len1):
        for j in range(1, len2):
            cost = 0 if string1[i - 1] == string2[j - 1] else 1
            tbl[i, j] = min(tbl[i, j - 1] + 1, tbl[i - 1, j] + 1, tbl[i - 1, j - 1] + cost)

    return tbl[i, j]


def getasminfo(instr):
    return '[%s] Descripción: %s.\nMás info: %s' % (
        instr.mnemonic,
        instr.summary,
        instr.url)


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
        # Start running the bot
        updater.start_polling(clean=True)
    except Exception as inst:
        logger.critical("ERROR AL INICIAR EL DCUBABOT")
        logger.exception(inst)


if __name__ == '__main__':
    from tokenz import *
    main()
