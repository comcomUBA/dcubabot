#!/usr/bin/python3
# -*- coding: utf-8 -*-

# STL imports
import logging
import pytz
import datetime
import random
from contextlib import contextmanager
from time import sleep

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


import labos
import river
import conciertos
from telegram.constants import ChatAction

import models
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
bsasTz = pytz.timezone("America/Argentina/Buenos_Aires")


@contextmanager
def get_session():
    """Provide a transactional scope around a series of operations."""
    if models.Session is None:
        models.init_db()
    session = models.Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola, ¿qué tal? ¡Mandame /help si no sabés qué puedo hacer!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = "Comandos disponibles:\n"
    with get_session() as session:
        commands = session.query(Command).filter_by(enabled=True).order_by(Command.name).all()
        for command in commands:
            if command.description:
                message_text += f"/{command.name} - {command.description}\n"
            else:
                message_text += f"/{command.name}\n"
    await update.message.reply_text(message_text)


async def estasvivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sí, estoy vivo.")


async def list_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, listable_type):
    with get_session() as session:
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


async def listar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await list_buttons(update, context, Grupo)


async def listaroptativa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await list_buttons(update, context, GrupoOptativa)


async def listareci(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await list_buttons(update, context, ECI)


async def listarotro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await list_buttons(update, context, GrupoOtros)


async def cubawiki(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_session() as session:
        group = session.query(Obligatoria).filter(
            Obligatoria.chat_id == str(update.message.chat.id),
            Obligatoria.cubawiki_url != None
        ).first()
        if group:
            await update.message.reply_text(group.cubawiki_url)


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

    with get_session() as session:
        group = listable_type(name=name, url=url)
        session.add(group)
        session.flush()
        group_id = group.id

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
    await update.message.reply_text("Este comando esta deprecado, para agregar un grupo por favor agregá el bot al grupo y escribí /agregargrupo")


async def sugeriroptativa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Este comando esta deprecado, para agregar un grupo por favor agregá el bot al grupo y escribí /agregaroptativa")


async def sugerireci(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Este comando esta deprecado, para agregar un grupo por favor agregá el bot al grupo y escribí /agregareci")


async def sugerirotro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Este comando esta deprecado, para agregar un grupo por favor agregá el bot al grupo y escribí /agregarotro")


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
    with get_session() as session:
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


# Manda un documento a partir de su path al chat del update dado
async def mandar_pdf(chat_id, context: ContextTypes.DEFAULT_TYPE, file_path):
    await context.bot.send_chat_action(
        chat_id=chat_id, action=ChatAction.UPLOAD_DOCUMENT)
    with get_session() as session:
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
    
    with get_session() as session:
        if buttonType == "Listable":
            group = session.query(Listable).filter_by(id=int(id)).first()
            if group:
                if action == "1":
                    group.validated = True
                    action_text = "\n¡Aceptado!"
                else:
                    session.delete(group)
                    action_text = "\n¡Rechazado!"
                await query.edit_message_text(text=message.text + action_text)
        
        elif buttonType == "Noticia":
            noticia = session.query(Noticia).filter_by(id=int(id)).first()
            if noticia:
                if action == "1":
                    noticia.validated = True
                    action_text = "\n¡Aceptado!"
                    await context.bot.send_message(chat_id=NOTICIAS_CHATID,
                                                   text=noticia.text, parse_mode=ParseMode.MARKDOWN)
                else:
                    session.delete(noticia)
                    action_text = "\n¡Rechazado!"
                await query.edit_message_text(text=message.text + action_text)


async def agregar(update: Update, context: ContextTypes.DEFAULT_TYPE, grouptype, groupString):
    try:
        url = await context.bot.export_chat_invite_link(
            chat_id=update.message.chat.id)
        name = update.message.chat.title
        chat_id = str(update.message.chat.id)
    except:  # TODO: filter excepts
        await update.message.reply_text(
            text=f"Mirá, no puedo hacerle un link a este grupo, proba haciendome admin")
        return
    with get_session() as session:
        group = session.query(grouptype).filter_by(chat_id=chat_id).first()
        if group:
            group.url = url
            group.name = name
            await update.message.reply_text(
                text=f"Datos del grupo actualizados")
            return
        group = grouptype(name=name, url=url, chat_id=chat_id)
        session.add(group)
        session.flush()
        group_id = group.id
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
                            text=f"{groupString}: {name}\n{url}",
                            reply_markup=reply_markup)
    await update.message.reply_text("OK, se lo mando a Rozen.")


async def agregargrupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await agregar(update, context, Grupo, "grupo")


async def agregaroptativa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await agregar(update, context, GrupoOptativa, "optativa")


async def agregarotros(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await agregar(update, context, GrupoOtros, "otro")


async def agregareci(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await agregar(update, context, ECI, "eci")


async def sugerirNoticia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name = user.first_name
    texto = " ".join(context.args)
    if not texto:
        await update.message.reply_text(
            text="Loc@, pusisiste algo mal, la idea es q pongas:\n "
                 "/sugerirNoticia <texto>")
        return
    with get_session() as session:
        noticia = Noticia(text=texto)
        session.add(noticia)
        session.flush()
        noticia_id = noticia.id
    keyboard = [
        [
            InlineKeyboardButton("Aceptar", callback_data=f"Noticia|{noticia_id}|1"),
            InlineKeyboardButton("Rechazar", callback_data=f"Noticia|{noticia_id}|0")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=ROZEN_CHATID, text=f"Noticia-{name}: {texto}",
                            reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    await update.message.reply_text(text="Ok, se lo pregunto a Rozen")


async def update_group_url(context: ContextTypes.DEFAULT_TYPE, chat_id: str) -> (str, str, bool):
    try:
        url = await context.bot.export_chat_invite_link(chat_id=chat_id)
        return chat_id, url, True  # too GO-like huh?
    except Exception:
        logger.error(f"Could not create invite link for {chat_id}", exc_info=True)
        return None, None, False  # too GO-like huh?


async def _update_groups(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Starting update_groups job")
    with get_session() as session:
        chats = list(session.query(Listable).filter_by(validated=True).all())
    logger.info(f"Found {len(chats)} groups to update")

    for chat in chats:
        sleep(1)
        chat_id, url, validated = await update_group_url(context, chat.chat_id)
        if not validated:
            logger.warning(f"Failed to update URL for group '{chat.name}'. De-validating.")
            with get_session() as session:
                c = session.query(Listable).filter_by(id=chat.id).first()
                c.validated = False
            await context.bot.send_message(chat_id=DC_GROUP_CHATID, text=f"El grupo {chat.name} murió 💀")
        else:
            logger.info(f"Updating URL for group '{chat.name}'")
            with get_session() as session:
                c = session.query(Listable).filter_by(id=chat.id).first()
                c.url = url
    logger.info("Finished update_groups job")


async def actualizar_grupos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Manual update of groups triggered by {update.effective_user.id}")
    await update.message.reply_text("Actualizando grupos...")
    await _update_groups(context)
    await update.message.reply_text("¡Grupos actualizados!")



async def mandar_imagen(chat_id: str, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
    file_id = None
    with get_session() as session:
        file_obj = session.query(File).filter_by(path=file_path).first()
        if file_obj:
            file_id = file_obj.file_id

    if file_id:
        try:
            msg = await context.bot.send_photo(chat_id=chat_id, photo=file_id)
            return
        except Exception:
            pass # if file_id is invalid, upload again

    with open(file_path, 'rb') as photo:
        msg = await context.bot.send_photo(chat_id=chat_id, photo=photo)
    
    with get_session() as session:
        file_obj = session.query(File).filter_by(path=file_path).first()
        if not file_obj:
            file_obj = File(path=file_path, file_id=msg.photo[-1].file_id)
            session.add(file_obj)
        else:
            file_obj.file_id = msg.photo[-1].file_id

async def mandar_pdf(chat_id: str, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_DOCUMENT)
    file_id = None
    with get_session() as session:
        file_obj = session.query(File).filter_by(path=file_path).first()
        if file_obj:
            file_id = file_obj.file_id

    if file_id:
        try:
            msg = await context.bot.send_document(chat_id=chat_id, document=file_id)
            return
        except Exception:
            pass # upload again

    with open(file_path, 'rb') as doc:
        msg = await context.bot.send_document(chat_id=chat_id, document=doc)
    
    with get_session() as session:
        file_obj = session.query(File).filter_by(path=file_path).first()
        if not file_obj:
            file_obj = File(path=file_path, file_id=msg.document.file_id)
            session.add(file_obj)
        else:
            file_obj.file_id = msg.document.file_id
            
async def responder_imagen(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    await mandar_imagen(update.message.chat_id, context, file_path)

async def responder_documento(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    await mandar_pdf(update.message.chat_id, context, file_path)

async def listarlabos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    mins = int(args[0]) if len(args) > 0 else 0
    instant = labos.aware_now() + datetime.timedelta(minutes=mins)
    respuesta = '\n'.join(labos.events_at(instant))
    await update.message.reply_text(text=respuesta)

async def flan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await responder_imagen(update, context, 'files/Plandeestudios-23.png')

async def flanviejo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await responder_imagen(update, context, 'files/Plandeestudios-93.png')

async def aulas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await responder_documento(update, context, 'files/0I-aulas.pdf')

def felizdia_text(today):
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
             "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    dia = str(today.day)
    mes = int(today.month)

    if mes == 3 and today.day == 8:
        return "Hoy es 8 de Marzo"
    else:
        mes = meses[mes - 1]
        return "Feliz " + dia + " de " + mes

async def felizdia(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.date.today()
    chat_id = ROZEN_CHATID
    await context.bot.send_message(chat_id=chat_id, text=felizdia_text(today))

async def actualizarPartidos(context: ContextTypes.DEFAULT_TYPE):
    hoy = datetime.datetime.now(bsasTz)
    mañana = hoy + datetime.timedelta(days=1)
    try:
        local, partido = river.es_local(mañana)
        if not local:
            return
        horario = "hora a confirmar" if partido.hora is None else partido.hora.strftime("a las %H:%M")
        msg = f"Mañana juega River, {horario}\n(contra {partido.equipo_visitante}, {partido.copa})"
        await context.bot.send_message(chat_id=NOTICIAS_CHATID, text=msg)
    except Exception as e:
        logger.error(f"Error checking River matches: {e}")

async def actualizarConciertos(context: ContextTypes.DEFAULT_TYPE):
    hoy = datetime.datetime.now(bsasTz)
    mañana = hoy + datetime.timedelta(days=1)
    try:
        hay, concierto = conciertos.hay_concierto(mañana)
        if not hay:
            return
        msg = f"Mañana hay un concierto en River\n{concierto.titulo}"
        await context.bot.send_message(chat_id=NOTICIAS_CHATID, text=msg)
    except Exception as e:
        logger.error(f"Error checking concerts: {e}")

async def actualizarRiver(context: ContextTypes.DEFAULT_TYPE):
    await actualizarPartidos(context)
    await actualizarConciertos(context)


COMMANDS = {

    'listarlabos': {
        'handler': listarlabos,
        'description': 'Muestra las reservas de los laboratorios.'
    },
    'flan': {
        'handler': flan,
        'description': 'Muestra el plan de estudios (2023).'
    },
    'flanviejo': {
        'handler': flanviejo,
        'description': 'Muestra el plan de estudios (1993).'
    },
    'aulas': {
        'handler': aulas,
        'description': 'Muestra el mapa de las aulas.'
    },
    'start': {
        'handler': start,
        'description': 'Inicia el bot.'
    },
    'help': {
        'handler': help_command,
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

    'agregargrupo': {
        'handler': agregargrupo,
        'description': 'Agrega el grupo actual a la lista de grupos de materias obligatorias.'
    },
    'agregaroptativa': {
        'handler': agregaroptativa,
        'description': 'Agrega el grupo actual a la lista de grupos de materias optativas.'
    },
    'agregareci': {
        'handler': agregareci,
        'description': 'Agrega el grupo actual a la lista de grupos de ECI.'
    },
    'agregarotros': {
        'handler': agregarotros,
        'description': 'Agrega el grupo actual a la lista de otros grupos.'
    },
    'sugerirnoticia': {
        'handler': sugerirNoticia,
        'description': 'Sugiere una noticia para el canal de noticias.'
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
    'actualizar_grupos': {
        'handler': actualizar_grupos,
        'description': 'Actualiza los links de todos los grupos.'
    },
    #deprecated
    'sugerirgrupo': {
        'handler': sugerirgrupo,
    },
    'sugeriroptativa': {
        'handler': sugeriroptativa,
    },
    'sugerireci': {
        'handler': sugerireci,
    },
    'sugerirotro': {
        'handler': sugerirotro,
    },
    #hidden

}
