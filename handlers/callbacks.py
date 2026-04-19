from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from models import Listable, Noticia
from handlers.db import get_session
from tg_ids import NOTICIAS_CHATID

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    message = query.message
    buttonType, id_val, action = query.data.split("|")
    
    with get_session() as session:
        if buttonType == "Listable":
            group = session.query(Listable).filter_by(id=int(id_val)).first()
            if group:
                if action == "1":
                    group.validated = True
                    action_text = "\n¡Aceptado!"
                else:
                    session.delete(group)
                    action_text = "\n¡Rechazado!"
                await query.edit_message_text(text=message.text + action_text)
        
        elif buttonType == "Noticia":
            noticia = session.query(Noticia).filter_by(id=int(id_val)).first()
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
