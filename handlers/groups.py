import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models import Grupo, GrupoOptativa, ECI, GrupoOtros, Obligatoria, Listable
from handlers.db import get_session
from tg_ids import ROZEN_CHATID, DC_GROUP_CHATID

logger = logging.getLogger("DCUBABOT")

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
            InlineKeyboardButton(text="Aceptar", callback_data=f"Listable|{group_id}|1", style="success"),
            InlineKeyboardButton(text="Rechazar", callback_data=f"Listable|{group_id}|0", style="danger")
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


async def agregar(update: Update, context: ContextTypes.DEFAULT_TYPE, grouptype, groupString):
    try:
        url = await context.bot.export_chat_invite_link(
            chat_id=update.message.chat.id)
        name = update.message.chat.title
        chat_id = str(update.message.chat.id)
    except:
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
            InlineKeyboardButton(text="Aceptar", callback_data=f"Listable|{group_id}|1", style="success"),
            InlineKeyboardButton(text="Rechazar", callback_data=f"Listable|{group_id}|0", style="danger")
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

from telegram.error import Forbidden, BadRequest, RetryAfter

async def update_group_url(context: ContextTypes.DEFAULT_TYPE, chat_id: str) -> tuple[str, str, bool]:
    try:
        url = await context.bot.export_chat_invite_link(chat_id=chat_id)
        return chat_id, url, True
    except (Forbidden, BadRequest) as e:
        logger.error(f"Bot is no longer allowed to create invite link for {chat_id}: {e}")
        return None, None, False
    except RetryAfter as e:
        logger.warning(f"Rate limited while creating invite link for {chat_id}. Retry after {e.retry_after} seconds.")
        return None, None, None
    except Exception as e:
        logger.error(f"Could not create invite link for {chat_id}: {e}", exc_info=True)
        return None, None, None

async def _update_groups(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Starting update_groups job")
    with get_session() as session:
        chats = [(c.id, c.chat_id, c.name) for c in session.query(Listable).filter_by(validated=True).filter(Listable.chat_id != None, Listable.chat_id != '').all()]
    logger.info(f"Found {len(chats)} groups to update")

    for chat_db_id, chat_chat_id, chat_name in chats:
        await asyncio.sleep(1)
        chat_id, url, validated = await update_group_url(context, chat_chat_id)
        if validated is False:
            logger.warning(f"Failed to update URL for group '{chat_name}'. De-validating.")
            with get_session() as session:
                c = session.query(Listable).filter_by(id=chat_db_id).first()
                if c:
                    c.validated = False
            try:
                await context.bot.send_message(chat_id=DC_GROUP_CHATID, text=f"El grupo {chat_name} murió 💀")
            except Exception as e:
                logger.error(f"Failed to send death message for {chat_name}: {e}")
        elif validated is True:
            logger.info(f"Updating URL for group '{chat_name}'")
            with get_session() as session:
                c = session.query(Listable).filter_by(id=chat_db_id).first()
                if c:
                    c.url = url
    logger.info("Finished update_groups job")

from handlers.admin import admin_ids

async def actualizar_grupos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in admin_ids and str(user_id) not in admin_ids:
        logger.warning(f"Unauthorized user {user_id} tried to access /actualizar_grupos")
        return
        
    logger.info(f"Manual update of groups triggered by {user_id}")
    await update.message.reply_text("Actualizando grupos (esto puede demorar varios minutos)...")
    await _update_groups(context)
    await update.message.reply_text("¡Grupos actualizados!")
