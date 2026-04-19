import sys
from telegram import Update
from telegram.ext import ContextTypes
from models import Command
from handlers.db import get_session

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
    await update.message.reply_text(f"Sí, estoy vivo y corriendo en Python {sys.version.split()[0]}")

async def colaborar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Se puede colaborar con el DCUBA bot en https://github.com/comcomUBA/dcubabot")
