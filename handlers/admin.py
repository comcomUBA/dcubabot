import logging
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from tg_ids import CODEPERS_CHATID, ROZEN_CHATID, DGARRO_CHATID
from models import Noticia
from handlers.db import get_session

logger = logging.getLogger("DCUBABOT")
admin_ids = [ROZEN_CHATID, DGARRO_CHATID]

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
    await update.message.reply_text("OK, se lo mando a les codepers.")

async def checodeppers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await checodepers(update, context)

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
            InlineKeyboardButton("Aceptar", callback_data=f"Noticia|{noticia_id}|1", style="success"),
            InlineKeyboardButton("Rechazar", callback_data=f"Noticia|{noticia_id}|0", style="danger")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=ROZEN_CHATID, text=f"Noticia-{name}: {texto}",
                            reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    await update.message.reply_text(text="Ok, se lo pregunto a Rozen")

async def get_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in admin_ids and str(user_id) not in admin_ids:
        logger.warning(f"Unauthorized user {user_id} tried to access /logs")
        return
    
    try:
        from google.cloud import logging as gcp_logging
        import json
        import io
        
        await update.message.reply_text("Buscando errores en Google Cloud Logging...")
        client = gcp_logging.Client()
        
        filter_str = 'severity>=ERROR AND (resource.type="cloud_run_revision" OR resource.type="cloud_run_job")'
        entries = client.list_entries(filter_=filter_str, order_by=gcp_logging.DESCENDING, max_results=50)
        
        log_msgs = []
        for entry in entries:
            log_data = {
                "timestamp": entry.timestamp.isoformat(),
                "severity": entry.severity,
            }
            
            payload = entry.payload
            if isinstance(payload, dict):
                log_data["json_payload"] = payload
            elif payload is not None:
                log_data["text_payload"] = str(payload)
            else:
                log_data["resource"] = str(entry.resource)
                
            log_msgs.append(log_data)
            
        if not log_msgs:
            await update.message.reply_text("✅ No se encontraron errores recientes en GCP.")
            return
            
        logs_json_str = json.dumps(log_msgs, indent=2, ensure_ascii=False)
        file_obj = io.BytesIO(logs_json_str.encode('utf-8'))
        file_obj.name = f"gcp_error_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=file_obj,
            caption="Acá tenés el archivo con los últimos errores registrados en GCP 🕵️‍♂️"
        )
    except Exception as e:
        await update.message.reply_text(f"Error al leer logs (¿falta permiso roles/logging.viewer en la Service Account?): {e}")
