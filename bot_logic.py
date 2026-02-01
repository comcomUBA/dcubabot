#!/usr/bin/python3
# -*- coding: utf-8 -*-

# STL imports
import logging
import pytz
import datetime
import random

# Non STL imports
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from typing import Dict, Final

# Local imports
from models import (Session, Command, Grupo, GrupoOptativa, ECI, GrupoOtros,
                    Obligatoria, Optativa, Otro, File, Listable, Noticia)
from deletablecommandhandler import DeletableCommandHandler
import labos
import river
import conciertos
from campus import is_campus_up

from vencimientoFinales import calcular_vencimiento, parse_cuatri_y_anio
from orga2Utils import noitip, asm
from tg_ids import DC_GROUP_CHATID, ROZEN_CHATID, DGARRO_CHATID, CODEPERS_CHATID, NOTICIAS_CHATID

# Globals ...... yes, globals
logger = logging.getLogger("DCUBABOT")
admin_ids = [ROZEN_CHATID, DGARRO_CHATID]  # @Rozen, @dgarro
command_handlers = {}
bsasTz = pytz.timezone("America/Argentina/Buenos_Aires")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola, ¿qué tal? ¡Mandame /help si no sabés qué puedo hacer!")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = "Comandos disponibles:\n"
    for name, command_info in sorted(COMMANDS.items()):
        if 'description' in command_info and command_info['description']:
            message_text += f"/{name} - {command_info['description']}\n"
    await update.message.reply_text(message_text)


async def estasvivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sí, estoy vivo.")


async def list_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, listable_type):
    session = Session()
    try:
        buttons = session.query(listable_type).filter_by(validated=True).order_by(listable_type.name).all()
        keyboard = []
        columns = 3
        for k in range(0, len(buttons), columns):
            row = [InlineKeyboardButton(
                text=button.name, url=button.url, callback_data=button.url)
                for button in buttons[k:k + columns]]

            keyboard.append(row)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text="Grupos: ", disable_web_page_preview=True,
                                        reply_markup=reply_markup)
    finally:
        session.close()


async def listar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await list_buttons(update, context, Grupo)


async def listaroptativa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await list_buttons(update, context, GrupoOptativa)


async def listareci(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await list_buttons(update, context, ECI)


async def listarotro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await list_buttons(update, context, GrupoOtros)


async def cubawiki(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    try:
        group = session.query(Obligatoria).filter(
            Obligatoria.chat_id == str(update.message.chat.id),
            Obligatoria.cubawiki_url != None
        ).first()
        if group:
            await update.message.reply_text(group.cubawiki_url)
    finally:
        session.close()


async def suggest_listable(update: Update, context: ContextTypes.DEFAULT_TYPE, listable_type):
    try:
        name, url = " ".join(context.args).split("|")
        if not (name and url):
            raise Exception("not userneim")
    except Exception:
        await update.message.reply_text("Hiciste algo mal, la idea es que pongas:\n" +
                                        update.message.text.split()[0] +
                                        " <nombre>|<link>")
        return

    session = Session()
    try:
        group = listable_type(name=name, url=url)
        session.add(group)
        session.commit()
        group_id = group.id
    finally:
        session.close()

    keyboard = [
        [
            InlineKeyboardButton(
                text="Aceptar", callback_data=f"Listable|{group_id}|1"),
            InlineKeyboardButton(
                text="Rechazar", callback_data=f"Listable|{group_id}|0")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=ROZEN_CHATID,
                            text=listable_type.__name__ + ": " + name + "\n" + url,
                            reply_markup=reply_markup)
    await update.message.reply_text("OK, se lo mando a Rozen.")


async def sugerirgrupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await suggest_listable(update, context, Obligatoria)


async def sugeriroptativa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await suggest_listable(update, context, Optativa)


async def sugerireci(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await suggest_listable(update, context, ECI)


async def sugerirotro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await suggest_listable(update, context, Otro)

async def agregargrupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Para sugerir un grupo, usá uno de los siguientes comandos, dependiendo de la categoría del grupo:\n"
        "/sugerirgrupo - Materia obligatoria\n"
        "/sugeriroptativa - Materia optativa\n"
        "/sugerireci - ECI\n"
        "/sugerirotro - Otra categoría\n\n"
        "El formato es: /comando <nombre>|<link>"
    )

async def campusvivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Bancá que me fijo...")

    campus_response_text = is_campus_up()

    await context.bot.edit_message_text(chat_id=msg.chat_id,
                                message_id=msg.message_id,
                                text=msg.text + "\n" + campus_response_text)


async def flan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await responder_imagen(update, context, 'files/Plandeestudios-23.png')

async def flanviejo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await responder_imagen(update, context, 'files/Plandeestudios-93.png')

async def aulas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await responder_documento(update, context, 'files/0I-aulas.pdf')

async def checodepers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        ejemplo = """ Ejemplo de uso:
  /checodepers Hola, tengo un mensaje mucho muy importante que me gustaria que respondan
"""
        await update.message.reply_text(ejemplo)
        return
    user = update.message.from_user
    try:
        if not user.username:
            raise Exception("not userneim")
        message = " ".join(context.args)
        await context.bot.send_message(
            chat_id=CODEPERS_CHATID, text=f"{user.first_name}(@{user.username}) : {message}")
    except Exception:
        try:
            await context.bot.forward_message(
                CODEPERS_CHATID, update.message.chat_id, update.message.message_id)
            logger.info(f"Malio sal {str(user)}")
        except Exception as e:
            await update.message.reply_text(
                "La verdad me re rompí, avisale a roz asi ve que onda")
            logger.error(e)
            return
    await update.message.reply_text(
        "OK, se lo mando a les codepers.")


async def checodeppers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await checodepers(update, context)

async def cuandovence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ejemplo = "\nCuatris: 1c, 2c, i, inv, invierno, v, ver, verano.\nEjemplo: /cuandovence verano2010"
    if not context.args:
        ayuda = "Pasame cuatri y año en que aprobaste los TPs." + ejemplo
        await update.message.reply_text(ayuda)
        return
    try:
        linea_entrada = "".join(context.args).lower()
        cuatri, anio = parse_cuatri_y_anio(linea_entrada)
    except Exception:
        await update.message.reply_text(
            "¿Me pasás las cosas bien? Es cuatri+año." + ejemplo)
        return

    vencimiento = calcular_vencimiento(cuatri, anio)
    await update.message.reply_text(
        vencimiento, parse_mode=ParseMode.MARKDOWN,disable_web_page_preview=True)


async def colaborar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Se puede colaborar con el DCUBA bot en https://github.com/comcomUBA/dcubabot")

# Manda una imagen a partir de su path al chat del update dado
async def mandar_imagen(chat_id, context: ContextTypes.DEFAULT_TYPE, file_path):
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
    session = Session()
    try:
        file = session.query(File).filter_by(path=file_path).first()
        if file:
            msg = await context.bot.send_photo(
                chat_id=chat_id, photo=file.file_id, allow_sending_without_reply=True)
        else:
            with open(file_path, 'rb') as f:
                msg = await context.bot.send_photo(
                    chat_id=chat_id, photo=f, allow_sending_without_reply=True)
            new_file = File(path=file_path, file_id=msg.photo[0].file_id)
            session.add(new_file)
            session.commit()
    finally:
        session.close()


# Manda un documento a partir de su path al chat del update dado
async def mandar_pdf(chat_id, context: ContextTypes.DEFAULT_TYPE, file_path):
    await context.bot.send_chat_action(
        chat_id=chat_id, action=ChatAction.UPLOAD_DOCUMENT)
    session = Session()
    try:
        file = session.query(File).filter_by(path=file_path).first()
        if file:
            msg = await context.bot.send_document(
                chat_id=chat_id, document=file.file_id, allow_sending_without_reply=True)
        else:
            with open(file_path, 'rb') as f:
                msg = await context.bot.send_document(
                    chat_id=chat_id, document=f, allow_sending_without_reply=True)
            new_file = File(path=file_path, file_id=msg.document.file_id)
            session.add(new_file)
            session.commit()
    finally:
        session.close()


# Responde una imagen a partir de su path al chat del update dado
async def responder_imagen(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path):
    await mandar_imagen(update.message.chat_id, context, file_path)

# Responde un documento a partir de su path al chat del update dado
async def responder_documento(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path):
    await mandar_pdf(update.message.chat_id, context, file_path)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    message = query.message
    buttonType, id, action = query.data.split("|")
    
    session = Session()
    try:
        if buttonType == "Listable":
            group = session.query(Listable).filter_by(id=int(id)).first()
            if group:
                if action == "1":
                    group.validated = True
                    session.commit()
                    action_text = "\n¡Aceptado!"
                else:
                    session.delete(group)
                    session.commit()
                    action_text = "\n¡Rechazado!"
                await query.edit_message_text(text=message.text + action_text)
        
        elif buttonType == "Noticia":
            noticia = session.query(Noticia).filter_by(id=int(id)).first()
            if noticia:
                if action == "1":
                    noticia.validated = True
                    session.commit()
                    action_text = "\n¡Aceptado!"
                    await context.bot.send_message(chat_id=NOTICIAS_CHATID,
                                                   text=noticia.text, parse_mode=ParseMode.MARKDOWN)
                else:
                    session.delete(noticia)
                    session.commit()
                    action_text = "\n¡Rechazado!"
                await query.edit_message_text(text=message.text + action_text)
    finally:
        session.close()


COMMANDS = {
    'start': {
        'handler': start,
        'description': 'Inicia el bot.'
    },
    'help': {
        'handler': help,
        'description': 'Muestra este mensaje de ayuda.'
    },
    'estasvivo': {
        'handler': estasvivo,
        'description': 'Responde si el bot está funcionando.'
    },
    'listar': {
        'handler': listar,
        'description': 'Muestra los grupos de Telegram de materias obligatorias.'
    },
    'listaroptativa': {
        'handler': listaroptativa,
        'description': 'Muestra los grupos de Telegram de materias optativas.'
    },
    'listareci': {
        'handler': listareci,
        'description': 'Muestra los grupos de Telegram de las ECI.'
    },
    'listarotro': {
        'handler': listarotro,
        'description': 'Muestra otros grupos de Telegram.'
    },
    'cubawiki': {
        'handler': cubawiki,
        'description': 'Devuelve el link a la Cubawiki de la materia (si estás en el grupo de la materia).'
    },
    'sugerirgrupo': {
        'handler': sugerirgrupo,
        'description': 'Sugiere un grupo de una materia obligatoria.'
    },
    'sugeriroptativa': {
        'handler': sugeriroptativa,
        'description': 'Sugiere un grupo de una materia optativa.'
    },
    'sugerireci': {
        'handler': sugerireci,
        'description': 'Sugiere un grupo de una ECI.'
    },
    'sugerirotro': {
        'handler': sugerirotro,
        'description': 'Sugiere un grupo de otra categoría.'
    },
    'campusvivo': {
        'handler': campusvivo,
        'description': 'Verifica si el Campus Virtual está funcionando.'
    },
    'noitip': {
        'handler': noitip,
        'description': "Explica el meme 'No, it IP'."
    },
    'asm': {
        'handler': asm,
        'description': 'Explica el meme de Assembly.'
    },
    'flan': {
        'handler': flan,
        'description': 'Muestra el plan de estudios de la carrera.'
    },
    'flanviejo': {
        'handler': flanviejo,
        'description': 'Muestra el plan de estudios viejo de la carrera.'
    },
    # 'aulas': {
    #     'handler': aulas,
    #     'description': 'Muestra el mapa de las aulas.'
    # },
    'checodepers': {
        'handler': checodepers,
        'description': 'Envía un mensaje a les codepers.'
    },
    'checodeppers': {
        'handler': checodeppers,
        'description': 'Alias para /checodepers.'
    },
    'cuandovence': {
        'handler': cuandovence,
        'description': 'Calcula cuándo vence la validez de los TPs de una materia.'
    },
    'colaborar': {
        'handler': colaborar,
        'description': 'Muestra el link al repositorio de Github del bot.'
    },
}
