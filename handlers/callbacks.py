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
    
    # Parse button data safely
    data_parts = query.data.split("|")
    buttonType = data_parts[0]
    id_val = data_parts[1] if len(data_parts) > 1 else None
    action = data_parts[2] if len(data_parts) > 2 else None
    
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
            else:
                await query.edit_message_text(text=message.text + "\n[Botón huérfano: El grupo ya no existe en la base de datos]")
                
        elif buttonType == "MoverGrupo":
            if action == "Cancelar":
                await query.edit_message_text(text=f"❌ Operación cancelada para el grupo ID {id_val}.")
                return
                
            group = session.query(Listable).filter_by(id=int(id_val)).first()
            if group:
                old_type = group.type
                new_type = action
                # Update the polymorphic identity directly via the type column
                group.type = new_type
                # Depending on SQLAlchemy, modifying the polymorphic column directly might require 
                # a raw SQL update or session.flush() to be safe. We'll rely on SQLAlchemy's update.
                await query.edit_message_text(text=f"✅ Grupo *{group.name}* movido exitosamente:\nDe `{old_type}` ➡️ a `{new_type}`", parse_mode=ParseMode.MARKDOWN)
            else:
                await query.edit_message_text(text=message.text + "\n[Botón huérfano: El grupo ya no existe]")
        
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
            else:
                await query.edit_message_text(text=message.text + "\n[Botón huérfano: La noticia ya no existe en la base de datos]")
