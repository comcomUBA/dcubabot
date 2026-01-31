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
}

def handle_command(update, bot):
    command_text = update.message.text.split(' ')[0][1:]
    command = command_text.split('@')[0] # Remove bot username from command
    if command in COMMANDS:
        context = DummyContext(bot, update)
        COMMANDS[command](update, context)
