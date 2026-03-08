#!/usr/bin/python3

# STL imports
import datetime
import logging
import random

import pytz

# Non STL imports
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

import conciertos
import labos
import river
from campus import is_campus_up
from deletablecommandhandler import DeletableCommandHandler

# Local imports
# from tokenz import *
from handlers.update_groups import actualizar_grupos, update_groups
from models import (
    ECI,
    Command,
    File,
    Grupo,
    GrupoOptativa,
    GrupoOtros,
    Listable,
    Noticia,
    Obligatoria,
    Optativa,
    Otro,
    commit,
    db_session,
    init_db,
)
from orga2Utils import asm, noitip  # noqa: F401 - used via globals()
from tg_ids import (
    CODEPERS_CHATID,
    DC_GROUP_CHATID,
    DGARRO_CHATID,
    NOTICIAS_CHATID,
    ROZEN_CHATID,
)
from utils.hora_feliz_dia import get_hora_feliz_dia, get_hora_update_groups
from vencimientoFinales import calcular_vencimiento, parse_cuatri_y_anio

# TODO:Move this out of here
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s",
    filename="bots.log",
)
# Globals ...... yes, globals
logger = logging.getLogger("DCUBABOT")
admin_ids = [ROZEN_CHATID, DGARRO_CHATID]  # @Rozen, @dgarro
command_handlers: dict[str, object] = {}
bsasTz = pytz.timezone("America/Argentina/Buenos_Aires")


async def error_callback(update, context):
    logger.exception(context.error)


async def start(update, context):
    msg = await update.message.reply_text(
        "Hola, ¿qué tal? ¡Mandame /help si no sabés qué puedo hacer!",
        do_quote=False,
    )
    context.sent_messages.append(msg)


async def help(update, context):
    message_text = ""
    with db_session:
        for command in list(Command.select(lambda c: c.enabled).order_by(lambda c: c.name)):
            if not command.description:
                continue
            message_text += "/" + command.name + " - " + command.description + "\n"
    msg = await update.message.reply_text(message_text, do_quote=False)
    context.sent_messages.append(msg)


async def estasvivo(update, context):
    msg = await update.message.reply_text("Sí, estoy vivo.", do_quote=False)
    context.sent_messages.append(msg)


async def list_buttons(update, context, listable_type):
    with db_session:
        buttons = list(
            listable_type.select(lambda item: item.validated).order_by(
                lambda item: item.name,
            )
        )
        keyboard = []
        columns = 3
        for k in range(0, len(buttons), columns):
            row = [
                InlineKeyboardButton(
                    text=button.name,
                    url=button.url,
                    callback_data=button.url,
                )
                for button in buttons[k : k + columns]
            ]

            keyboard.append(row)
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = await update.message.reply_text(
            text="Grupos: ",
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            do_quote=False,
        )
        context.sent_messages.append(msg)


async def listar(update, context):
    await list_buttons(update, context, Grupo)


async def listaroptativa(update, context):
    await list_buttons(update, context, GrupoOptativa)


async def listareci(update, context):
    await list_buttons(update, context, ECI)


async def listarotro(update, context):
    await list_buttons(update, context, GrupoOtros)


async def cubawiki(update, context):
    chat_id = update.message.chat.id
    with db_session:
        for group in list(Obligatoria.select(lambda o: o.chat_id == chat_id)):
            if group.cubawiki_url is not None:
                msg = await update.message.reply_text(group.cubawiki_url, do_quote=False)
                context.sent_messages.append(msg)
                break


async def log_message(update, context):
    user = str(update.message.from_user.id)
    chat = str(update.message.chat.id)
    # EAFP
    try:
        user_at_group = user + " @ " + update.message.chat.title
    except Exception:
        user_at_group = user
    user_at_group = f"{user_at_group}({chat})"
    logger.info("%s: %s", user_at_group, update.message.text)


def felizdia_text(today):
    meses = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]
    dia = str(today.day)
    mes = int(today.month)

    if mes == 3 and today.day == 8:
        return "Hoy es 8 de Marzo"
    mes = meses[mes - 1]
    return "Feliz " + dia + " de " + mes


async def felizdia(context):
    if random.uniform(0, 7) > 1:
        return
    today = datetime.date.today()
    chat_id = DC_GROUP_CHATID
    await context.bot.send_message(chat_id=chat_id, text=felizdia_text(today))


async def suggest_listable(update, context, listable_type):
    try:
        name, url = " ".join(context.args).split("|")
        if not (name and url):
            raise Exception("not userneim")
    except Exception:
        msg = await update.message.reply_text(
            "Hiciste algo mal, la idea es que pongas:\n"
            + update.message.text.split()[0]
            + " <nombre>|<link>",
            do_quote=False,
        )
        context.sent_messages.append(msg)
        return
    with db_session:
        group = listable_type(name=name, url=url)
    keyboard = [
        [
            InlineKeyboardButton(
                text="Aceptar",
                callback_data=f"Listable|{group.id}|1",
            ),
            InlineKeyboardButton(
                text="Rechazar",
                callback_data=f"Listable|{group.id}|0",
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=ROZEN_CHATID,
        text=listable_type.__name__ + ": " + name + "\n" + url,
        reply_markup=reply_markup,
    )
    msg = await update.message.reply_text("OK, se lo mando a Rozen.", do_quote=False)
    context.sent_messages.append(msg)


async def sugerirgrupo(update, context):
    await suggest_listable(update, context, Obligatoria)


async def sugeriroptativa(update, context):
    await suggest_listable(update, context, Optativa)


async def sugerireci(update, context):
    await suggest_listable(update, context, ECI)


async def sugerirotro(update, context):
    await suggest_listable(update, context, Otro)


async def listarlabos(update, context):
    args = context.args
    mins = int(args[0]) if len(args) > 0 else 0
    instant = labos.aware_now() + datetime.timedelta(minutes=mins)
    respuesta = "\n".join(labos.events_at(instant))
    msg = await update.message.reply_text(text=respuesta, do_quote=False)
    context.sent_messages.append(msg)


async def flan(update, context):
    await responder_imagen(update, context, "files/Plandeestudios-23.png")


async def flanviejo(update, context):
    await responder_imagen(update, context, "files/Plandeestudios-93.png")


async def aulas(update, context):
    await responder_documento(update, context, "files/0I-aulas.pdf")


async def togglecommand(update, context):
    if context.args and update.message and update.message.from_user.id in admin_ids:
        command_name = context.args[0]
        if command_name not in command_handlers:
            await update.message.reply_text(
                text=f"No existe el comando /{command_name}.",
                do_quote=False,
            )
            return
        with db_session:
            command = Command.get(name=command_name)
            command.enabled = not command.enabled
            if command.enabled:
                action = "activado"
                context.application.add_handler(command_handlers[command_name])
            else:
                action = "desactivado"
                context.application.remove_handler(command_handlers[command_name])
            await update.message.reply_text(
                text=f"Comando /{command_name} {action}.",
                do_quote=False,
            )


async def sugerir(update, context):
    await update.message.reply_text(
        text="Ahora en mas las sugerencias las vamos a tomar en github:\n "
        "https://github.com/comcomUBA/dcubabot/issues",
        do_quote=False,
    )


async def sugerirNoticia(update, context):
    user = update.message.from_user
    name = user.first_name  # Agarro el nombre para ver quien fue
    # /sugerirNoticia <texto>
    texto = str.join(" ", context.args)
    try:
        # Esto es re cabeza pero no me acuerdo por que está asi
        if not (texto and isinstance(texto, str)):
            raise Exception
    except Exception:
        await update.message.reply_text(
            text="Loc@, pusisiste algo mal, la idea es q pongas:\n /sugerirNoticia <texto>",
        )
        return
    try:
        with db_session:
            noticia = Noticia(text=texto)
            commit()  # Hago el commmit para que tenga un id
        keyboard = [
            [
                InlineKeyboardButton(
                    "Aceptar",
                    callback_data="Noticia|" + str(noticia.id) + "|1",
                ),
                InlineKeyboardButton(
                    "Rechazar",
                    callback_data="noticia|" + str(noticia.id) + "|0",
                ),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=ROZEN_CHATID,
            text=f"Noticia-{name}: {texto}",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN,
        )
        await update.message.reply_text(text="Ok, se lo pregunto a Rozen")
    except Exception as inst:
        logger.exception(inst)


# Manda una imagen a partir de su path al chat del update dado
async def mandar_imagen(chat_id, context, file_path):
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
    with db_session:
        file = File.get(path=file_path)
    if file:
        msg = await context.bot.send_photo(chat_id=chat_id, photo=file.file_id)
    else:
        with open(file_path, "rb") as f:  # noqa: ASYNC230  # noqa: ASYNC230  # noqa: ASYNC230
            msg = await context.bot.send_photo(chat_id=chat_id, photo=f)
        with db_session:
            File(path=file_path, file_id=msg.photo[0].file_id)


# Manda un documento a partir de su path al chat del update dado
async def mandar_pdf(chat_id, context, file_path):
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_DOCUMENT)
    with db_session:
        file = File.get(path=file_path)
    if file:
        msg = await context.bot.send_document(chat_id=chat_id, document=file.file_id)
    else:
        with open(file_path, "rb") as f:  # noqa: ASYNC230  # noqa: ASYNC230  # noqa: ASYNC230
            msg = await context.bot.send_document(chat_id=chat_id, document=f)
        with db_session:
            File(path=file_path, file_id=msg.document.file_id)


# Responde una imagen a partir de su path al chat del update dado
async def responder_imagen(update, context, file_path):
    await mandar_imagen(update.message.chat_id, context, file_path)


""" La funcion button se encarga de tomar todos los botones
    que se apreten en el bot (y que no sean links)"""


# TODO: Posiblemente usar Double Dispatch para ver como
# Cada Boton de validacion hace lo mismo o no


# Responde un documento a partir de su path al chat del update dado
async def responder_documento(update, context, file_path):
    await mandar_pdf(update.message.chat_id, context, file_path)


async def button(update, context):
    query = update.callback_query
    message = query.message
    buttonType, id, action = query.data.split("|")
    with db_session:
        if buttonType == "Listable":
            group = Listable[int(id)]
            if action == "1":
                group.validated = True
                action_text = "\n¡Aceptado!"
            else:
                group.delete()
                action_text = "\n¡Rechazado!"
            await context.bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=message.text + action_text,
            )
        if buttonType == "Noticia":
            noticia = Noticia[int(id)]
            if action == "1":
                noticia.validated = True
                action_text = "\n¡Aceptado!"
                await context.bot.send_message(
                    chat_id=NOTICIAS_CHATID,
                    text=noticia.text,
                    parse_mode=ParseMode.MARKDOWN,
                )
            else:
                noticia.delete()
                action_text = "\n¡Rechazado!"
            await context.bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=message.text + action_text,
            )


async def actualizarPartidos(context):
    hoy = datetime.datetime.now()
    mañana = hoy + datetime.timedelta(days=1)
    local, partido = river.es_local(mañana)

    if not local:
        return

    async def partido_msg(context):
        if partido.hora is None:
            horario = "hora a confirmar"
        else:
            horario = partido.hora.strftime("a las %H:%M")

        msg = f"Mañana juega River, {horario}"
        msg += f"\n(contra {partido.equipo_visitante}, {partido.copa})"

        await context.bot.send_message(chat_id=NOTICIAS_CHATID, text=msg)

    # la hora local es UTC así que especificamos el timezone que corresponde para el aviso acá
    avisoHora = hoy.replace(hour=20, tzinfo=bsasTz)  # 8pm argentina, buenos aires
    context.job_queue.run_once(callback=partido_msg, when=avisoHora)


async def actualizarConciertos(context):
    hoy = datetime.datetime.now()
    mañana = hoy + datetime.timedelta(days=1)
    hay_concierto, concierto = conciertos.hay_concierto(mañana)

    if not hay_concierto:
        return

    async def concierto_msg(context):
        msg = f"Mañana hay un concierto en River\n{concierto.titulo}"
        await context.bot.send_message(chat_id=NOTICIAS_CHATID, text=msg)

    avisoHora = hoy.replace(hour=20, tzinfo=bsasTz)  # 8pm argentina, buenos aires
    context.job_queue.run_once(callback=concierto_msg, when=avisoHora)


async def actualizarRiver(context):
    await actualizarPartidos(context)
    await actualizarConciertos(context)


def add_all_handlers(application: Application):
    descriptions = []
    application.add_handler(
        MessageHandler((filters.TEXT | filters.COMMAND), log_message),
        group=1,
    )
    with db_session:
        for command in list(Command.select(lambda _: True)):
            handler = DeletableCommandHandler(command.name, globals()[command.name])
            command_handlers[command.name] = handler
            if command.enabled:
                application.add_handler(handler)
                if command.description:
                    descriptions.append((command.name, command.description))
    application.add_handler(CallbackQueryHandler(button))
    print(descriptions)
    return descriptions


def _make_post_init(descriptions):
    async def _set_commands(app: Application):
        await app.bot.set_my_commands(descriptions)

    return _set_commands


async def checodepers(update, context):
    if not context.args:
        ejemplo = """ Ejemplo de uso:
  /checodepers Hola, tengo un mensaje mucho muy importante que me gustaria que respondan
"""
        msg = await update.message.reply_text(ejemplo, do_quote=False)
        context.sent_messages.append(msg)
        return
    user = update.message.from_user
    try:
        if not user.username:
            raise Exception("not userneim")
        message = " ".join(context.args)
        await context.bot.send_message(
            chat_id=CODEPERS_CHATID,
            text=f"{user.first_name}(@{user.username}) : {message}",
        )
    except Exception:
        try:
            await context.bot.forward_message(
                chat_id=CODEPERS_CHATID,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id,
            )
            logger.info(f"Malio sal {user!s}")
        except Exception as e:
            await update.message.reply_text(
                "La verdad me re rompí, avisale a roz asi ve que onda",
                do_quote=False,
            )
            logger.error(e)
            return
    msg = await update.message.reply_text("OK, se lo mando a les codepers.", do_quote=False)
    context.sent_messages.append(msg)


async def checodeppers(update, context):
    await checodepers(update, context)


async def campusvivo(update, context):
    msg = await update.message.reply_text("Bancá que me fijo...", do_quote=False)

    campus_response_text = is_campus_up()

    await context.bot.edit_message_text(
        chat_id=msg.chat_id,
        message_id=msg.message_id,
        text=msg.text + "\n" + campus_response_text,
    )

    context.sent_messages.append(msg)


async def cuandovence(update, context):
    ejemplo = (
        "\nCuatris: 1c, 2c, i, inv, invierno, v, ver, verano.\nEjemplo: /cuandovence verano2010"
    )
    if not context.args:
        ayuda = "Pasame cuatri y año en que aprobaste los TPs." + ejemplo
        msg = await update.message.reply_text(ayuda, do_quote=False)
        context.sent_messages.append(msg)
        return
    try:
        linea_entrada = "".join(context.args).lower()
        cuatri, anio = parse_cuatri_y_anio(linea_entrada)
    except Exception:
        msg = await update.message.reply_text(
            "¿Me pasás las cosas bien? Es cuatri+año." + ejemplo,
            do_quote=False,
        )
        context.sent_messages.append(msg)
        return

    vencimiento = calcular_vencimiento(cuatri, anio)
    msg = await update.message.reply_text(
        vencimiento,
        do_quote=False,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )
    context.sent_messages.append(msg)


async def colaborar(update, context):
    if update.message is None:
        return
    msg = await update.message.reply_text(
        "Se puede colaborar con el DCUBA bot en https://github.com/comcomUBA/dcubabot",
        do_quote=False,
    )
    context.sent_messages.append(msg)


async def agregar(update: Update, context: CallbackContext, grouptype, groupString):
    if update.message is None:
        return
    message = update.message
    try:
        url = await context.bot.export_chat_invite_link(chat_id=message.chat.id)
        name = message.chat.title
        chat_id = str(message.chat.id)
    except Exception:  # TODO: filter excepts
        await message.reply_text(
            text="Mirá, no puedo hacerle un link a este grupo, proba haciendome admin",
            do_quote=False,
        )
        return
    with db_session:
        group = grouptype.get(chat_id=chat_id)
        if group:
            group.url = url
            group.name = name
            await message.reply_text(text="Datos del grupo actualizados", do_quote=False)
            return
        group = grouptype(name=name, url=url, chat_id=chat_id)
    keyboard = [
        [
            InlineKeyboardButton(
                text="Aceptar",
                callback_data=f"Listable|{group.id}|1",
            ),
            InlineKeyboardButton(
                text="Rechazar",
                callback_data=f"Listable|{group.id}|0",
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=ROZEN_CHATID,
        text=f"{groupString}: {name}\n{url}",
        reply_markup=reply_markup,
    )
    msg = await message.reply_text("OK, se lo mando a Rozen.", do_quote=False)
    context.sent_messages.append(msg)


async def agregargrupo(update: Update, context: CallbackContext):
    await agregar(update, context, Grupo, "grupo")


async def agregaroptativa(update: Update, context: CallbackContext):
    await agregar(update, context, GrupoOptativa, "optativa")


async def agregarotros(update: Update, context: CallbackContext):
    await agregar(update, context, GrupoOtros, "otro")


async def agregareci(update: Update, context: CallbackContext):
    await agregar(update, context, ECI, "eci")


def main():
    try:
        # Telegram bot Authorization Token
        print("Iniciando DCUBABOT")
        logger.info("Iniciando")
        random.seed()
        init_db("dcubabot.sqlite3")
        with db_session:
            descriptions = [
                (c.name, c.description)
                for c in list(Command.select(lambda c: c.description is not None))
                if c.description and c.description.strip()
            ]
        application = (
            Application.builder()
            .token(token)
            .connect_timeout(30.0)
            .read_timeout(30.0)
            .post_init(_make_post_init(descriptions))
            .build()
        )

        add_all_handlers(application)

        application.job_queue.run_daily(callback=felizdia, time=get_hora_feliz_dia())
        application.job_queue.run_daily(
            callback=update_groups,
            time=get_hora_update_groups(),
        )

        application.job_queue.run_once(callback=actualizarRiver, when=0)
        application.job_queue.run_daily(callback=actualizarRiver, time=datetime.time())

        application.add_handler(CommandHandler("actualizar_grupos", actualizar_grupos))

        application.job_queue.run_repeating(
            callback=labos.update,
            interval=datetime.timedelta(hours=1),
        )
        application.add_error_handler(error_callback)

        print([j for j in application.job_queue.jobs()])
        application.run_polling(drop_pending_updates=True)
    except Exception as inst:
        logger.critical("ERROR AL INICIAR EL DCUBABOT")
        logger.exception(inst)


if __name__ == "__main__":
    from tokenz import token

    main()
