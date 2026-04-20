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
            sub_action = id_val
            value = action
            
            if sub_action == "Cancel":
                await query.edit_message_text(text="❌ Operación cancelada.")
                return
            elif sub_action == "Page":
                from handlers.admin import get_movergrupo_keyboard
                reply_markup = get_movergrupo_keyboard(session, page=int(value))
                await query.edit_message_text(
                    text="Seleccioná el grupo que querés recategorizar:",
                    reply_markup=reply_markup
                )
                return
            elif sub_action == "Select":
                group = session.query(Listable).filter_by(id=int(value)).first()
                if not group:
                    await query.edit_message_text(text="[Botón huérfano: El grupo ya no existe]")
                    return
                
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                keyboard = [
                    [
                        InlineKeyboardButton("Grupo (Oblig.)", callback_data=f"MoverGrupo|Move|{group.id}|Grupo", api_kwargs={"style": "primary"}),
                        InlineKeyboardButton("GrupoOptativa", callback_data=f"MoverGrupo|Move|{group.id}|GrupoOptativa", api_kwargs={"style": "primary"}),
                        InlineKeyboardButton("ECI", callback_data=f"MoverGrupo|Move|{group.id}|ECI", api_kwargs={"style": "primary"})
                    ],
                    [
                        InlineKeyboardButton("Otro", callback_data=f"MoverGrupo|Move|{group.id}|Otro", api_kwargs={"style": "primary"}),
                        InlineKeyboardButton("GrupoOtros", callback_data=f"MoverGrupo|Move|{group.id}|GrupoOtros", api_kwargs={"style": "primary"}),
                        InlineKeyboardButton("Obligatoria (v.)", callback_data=f"MoverGrupo|Move|{group.id}|Obligatoria", api_kwargs={"style": "primary"})
                    ],
                    [
                        InlineKeyboardButton("Optativa (v.)", callback_data=f"MoverGrupo|Move|{group.id}|Optativa", api_kwargs={"style": "primary"}),
                        InlineKeyboardButton("❌ Cancelar", callback_data="MoverGrupo|Cancel|0", api_kwargs={"style": "danger"})
                    ]
                ]
                await query.edit_message_text(
                    text=f"Seleccioná la nueva categoría para el grupo:\n\n*Nombre:* {group.name}\n*Categoría Actual:* {group.type}",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            elif sub_action == "Move":
                group_id = int(data_parts[2])
                new_type = data_parts[3]
                
                group = session.query(Listable).filter_by(id=group_id).first()
                if group:
                    old_type = group.type
                    group.type = new_type
                    await query.edit_message_text(text=f"✅ Grupo *{group.name}* movido exitosamente:\nDe `{old_type}` ➡️ a `{new_type}`", parse_mode=ParseMode.MARKDOWN)
                else:
                    await query.edit_message_text(text="[Botón huérfano: El grupo ya no existe]")
                return
        
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
