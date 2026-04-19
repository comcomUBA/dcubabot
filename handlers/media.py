from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from models import File
from handlers.db import get_session

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
