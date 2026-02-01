import telegram
import os
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from bot_logic import COMMANDS, button
from models import init_db

async def log_update(update, context):
    """Log every update received by the bot."""
    logger = logging.getLogger("DCUBABOT")
    user = update.effective_user
    chat = update.effective_chat
    
    log_message = f"Update received. User: {user.id} ({user.username}) in chat: {chat.id} ({chat.title})."
    if update.message and update.message.text:
        log_message += f" Message: {update.message.text}"
    elif update.callback_query:
        log_message += f" Callback Query: {update.callback_query.data}"
        
    logger.info(log_message)


def main():
    """Start the bot."""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s',
        filename="bots.log"
    )
    
    init_db()

    application = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()

    # Add the logging middleware handler with a high priority
    application.add_handler(MessageHandler(filters.ALL, log_update), group=-1)

    for command_name, command_info in COMMANDS.items():
        application.add_handler(CommandHandler(command_name, command_info['handler']))

    application.add_handler(CallbackQueryHandler(button))

    webhook_url = os.environ["WEBHOOK_URL"]
    
    # Start the Bot
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        url_path=os.environ["TELEGRAM_BOT_TOKEN"],
        webhook_url=f'{webhook_url.rstrip("/")}/{os.environ["TELEGRAM_BOT_TOKEN"]}',
    )

if __name__ == "__main__":
    main()
