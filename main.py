import telegram
import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from bot_logic import COMMANDS, button  # Assuming 'button' is now in bot_logic
from models import init_db

def main():
    """Start the bot."""

    application = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()


    for command_name, command_info in COMMANDS.items():
            application.add_handler(CommandHandler(command_name, command_info['handler']))

    # Register the callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button))


    init_db()

    # The WEBHOOK_URL is now guaranteed to be set by the CI/CD pipeline.
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
