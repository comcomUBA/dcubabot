#!/usr/bin/python3
# -*- coding: utf-8 -*-

# STL imports
import logging
import pytz
import datetime
import random

# Non STL imports
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction, ParseMode, Update
from telegram.ext import (
    Updater, Filters, MessageHandler, CallbackQueryHandler, CallbackContext, CommandHandler)
from typing import Dict, Final

# Local imports
from models import *
from deletablecommandhandler import DeletableCommandHandler
import labos
import river
import conciertos
from campus import is_campus_up
from utils.hora_feliz_dia import get_hora_feliz_dia, get_hora_update_groups
from vencimientoFinales import calcular_vencimiento, parse_cuatri_y_anio
from orga2Utils import noitip, asm
from tg_ids import DC_GROUP_CHATID, ROZEN_CHATID, DGARRO_CHATID, CODEPERS_CHATID, NOTICIAS_CHATID

# Globals ...... yes, globals
logger = logging.getLogger("DCUBABOT")
admin_ids = [ROZEN_CHATID, DGARRO_CHATID]  # @Rozen, @dgarro
command_handlers = {}
bsasTz = pytz.timezone("America/Argentina/Buenos_Aires")


class DummyContext:
    def __init__(self, bot, update):
        self.bot = bot
        self.update = update
        self.sent_messages = []
        self.args = update.message.text.split()[1:] # For commands with arguments

def start(update, context):
    msg = update.message.reply_text(
        "Hola, ¿qué tal? ¡Mandame /help si no sabés qué puedo hacer!",
        quote=False)
    context.sent_messages.append(msg)


def help(update, context):
    message_text = ""
    with db_session:
        for command in select(c for c in Command
                              if c.description and c.enabled).order_by(lambda c: c.name):
            message_text += "/" + command.name + " - " + command.description + "\n"
    msg = update.message.reply_text(message_text, quote=False)
    context.sent_messages.append(msg)


def estasvivo(update, context):
    msg = update.message.reply_text("Sí, estoy vivo.", quote=False)
    context.sent_messages.append(msg)


def list_buttons(update, context, listable_type):
    with db_session:
        buttons = select(l for l in listable_type if l.validated).order_by(
            lambda l: l.name)
        keyboard = []
        columns = 3
        for k in range(0, len(buttons), columns):
            row = [InlineKeyboardButton(
                text=button.name, url=button.url, callback_data=button.url)
                for button in buttons[k:k + columns]]

            keyboard.append(row)
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = update.message.reply_text(text="Grupos: ", disable_web_page_preview=True,
                                        reply_markup=reply_markup, quote=False)
        context.sent_messages.append(msg)


def listar(update, context):
    list_buttons(update, context, Grupo)


def listaroptativa(update, context):
    list_buttons(update, context, GrupoOptativa)


def listareci(update, context):
    list_buttons(update, context, ECI)


def listarotro(update, context):
    list_buttons(update, context, GrupoOtros)


def cubawiki(update, context):
    with db_session:
        group = select(o for o in Obligatoria if o.chat_id == update.message.chat.id and
                       o.cubawiki_url is not None).first()
        if group:
            msg = update.message.reply_text(group.cubawiki_url, quote=False)
            context.sent_messages.append(msg)


def suggest_listable(update, context, listable_type):
    try:
        name, url = " ".join(context.args).split("|")
        if not (name and url):
            raise Exception("not userneim")
    except Exception:
        msg = update.message.reply_text("Hiciste algo mal, la idea es que pongas:\n" +
                                        update.message.text.split()[0] +
                                        " <nombre>|<link>",
                                        quote=False)
        context.sent_messages.append(msg)
        return
    with db_session:
        group = listable_type(name=name, url=url)
    keyboard = [
        [
            InlineKeyboardButton(
                text="Aceptar", callback_data=f"Listable|{group.id}|1"),
            InlineKeyboardButton(
                text="Rechazar", callback_data=f"Listable|{group.id}|0")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.sendMessage(chat_id=ROZEN_CHATID,
                            text=listable_type.__name__ + ": " + name + "\n" + url,
                            reply_markup=reply_markup)
    msg = update.message.reply_text("OK, se lo mando a Rozen.", quote=False)
    context.sent_messages.append(msg)


def sugerirgrupo(update, context):
    suggest_listable(update, context, Obligatoria)


def sugeriroptativa(update, context):
    suggest_listable(update, context, Optativa)


def sugerireci(update, context):
    suggest_listable(update, context, ECI)


def sugerirotro(update, context):
    suggest_listable(update, context, Otro)

def campusvivo(update, context):
    msg = update.message.reply_text("Bancá que me fijo...", quote=False)

    campus_response_text = is_campus_up()

    context.bot.editMessageText(chat_id=msg.chat_id,
                                message_id=msg.message_id,
                                text=msg.text + "\n" + campus_response_text)

    context.sent_messages.append(msg)

def flan(update, context):
    responder_imagen(update, context, 'files/Plandeestudios.png')

def flanviejo(update, context):
    responder_imagen(update, context, 'files/Plandeestudios-93.png')

def aulas(update, context):
    responder_documento(update, context, 'files/0I-aulas.pdf')

def checodepers(update, context):
    if not context.args:
        ejemplo = """ Ejemplo de uso:
  /checodepers Hola, tengo un mensaje mucho muy importante que me gustaria que respondan
"""
        msg = update.message.reply_text(ejemplo, quote=False)
        context.sent_messages.append(msg)
        return
    user = update.message.from_user
    try:
        if not user.username:
            raise Exception("not userneim")
        message = " ".join(context.args)
        context.bot.sendMessage(
            chat_id=CODEPERS_CHATID, text=f"{user.first_name}(@{user.username}) : {message}")
    except Exception:
        try:
            context.bot.forward_message(
                CODEPERS_CHATID, update.message.chat_id, update.message.message_id)
            logger.info(f"Malio sal {str(user)}")
        except Exception as e:
            update.message.reply_text(
                "La verdad me re rompí, avisale a roz asi ve que onda", quote=False)
            logger.error(e)
            return
    msg = update.message.reply_text(
        "OK, se lo mando a les codepers.", quote=False)
    context.sent_messages.append(msg)


def checodeppers(update, context):
    checodepers(update, context)

def cuandovence(update, context):
    ejemplo = "\nCuatris: 1c, 2c, i, inv, invierno, v, ver, verano.\nEjemplo: /cuandovence verano2010"
    if not context.args:
        ayuda = "Pasame cuatri y año en que aprobaste los TPs." + ejemplo
        msg = update.message.reply_text(ayuda, quote=False)
        context.sent_messages.append(msg)
        return
    try:
        linea_entrada = "".join(context.args).lower()
        cuatri, anio = parse_cuatri_y_anio(linea_entrada)
    except Exception:
        msg = update.message.reply_text(
            "¿Me pasás las cosas bien? Es cuatri+año." + ejemplo, quote=False)
        context.sent_messages.append(msg)
        return

    vencimiento = calcular_vencimiento(cuatri, anio)
    msg = update.message.reply_text(
        vencimiento, quote=False, parse_mode=ParseMode.MARKDOWN,disable_web_page_preview=True)
    context.sent_messages.append(msg)


def colaborar(update, context):
    msg = update.message.reply_text(
        "Se puede colaborar con el DCUBA bot en https://github.com/comcomUBA/dcubabot", quote=False)
    context.sent_messages.append(msg)

# Manda una imagen a partir de su path al chat del update dado
def mandar_imagen(chat_id, context, file_path):
    context.bot.sendChatAction(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
    with db_session:
        file = File.get(path=file_path)
    if file:
        msg = context.bot.send_photo(
            chat_id=chat_id, photo=file.file_id, allow_sending_without_reply=True)
    else:
        msg = context.bot.send_photo(
            chat_id=chat_id, photo=open(file_path, 'rb'), allow_sending_without_reply=True)
        with db_session:
            File(path=file_path, file_id=msg.photo[0].file_id)

# Manda un documento a partir de su path al chat del update dado
def mandar_pdf(chat_id, context, file_path):
    context.bot.sendChatAction(
        chat_id=chat_id, action=ChatAction.UPLOAD_DOCUMENT)
    with db_session:
        file = File.get(path=file_path)
    if file:
        msg = context.bot.send_document(
            chat_id=chat_id, document=file.file_id, allow_sending_without_reply=True)
    else:
        msg = context.bot.send_document(
            chat_id=chat_id, document=open(file_path, 'rb'), allow_sending_without_reply=True)
        with db_session:
            File(path=file_path, file_id=msg.document[0].file_id)


# Responde una imagen a partir de su path al chat del update dado
def responder_imagen(update, context, file_path):
    mandar_imagen(update.message.chat_id, context, file_path)

# Responde un documento a partir de su path al chat del update dado
def responder_documento(update, context, file_path):
    mandar_pdf(update.message.chat_id, context, file_path)


COMMANDS = {
    'start': start,
    'help': help,
    'estasvivo': estasvivo,
    'listar': listar,
    'listaroptativa': listaroptativa,
    'listareci': listareci,
    'listarotro': listarotro,
    'cubawiki': cubawiki,
    'sugerirgrupo': sugerirgrupo,
    'sugeriroptativa': sugeriroptativa,
    'sugerireci': sugerireci,
    'sugerirotro': sugerirotro,
    'campusvivo': campusvivo,
    'noitip': noitip,
    'asm': asm,
    'flan': flan,
    'flanviejo': flanviejo,
#    'aulas': aulas, lo comente por q se me rompio mandar pdf y no se por q
    'checodepers': checodepers,
    'checodeppers': checodeppers,
    'cuandovence': cuandovence,
    'colaborar': colaborar,
}

def handle_command(update, bot):
    command_text = update.message.text.split(' ')[0][1:]
    command = command_text.split('@')[0] # Remove bot username from command
    if command in COMMANDS:
        context = DummyContext(bot, update)
        COMMANDS[command](update, context)
