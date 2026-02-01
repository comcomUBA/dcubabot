import telegram
import os
from telegram.ext import Application, CommandHandler
from bot_logic import COMMANDS
from models import init_db

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()

    # on different commands - answer in Telegram
    for command_name, command_handler in COMMANDS.items():
        application.add_handler(CommandHandler(command_name, command_handler))

    # Initialize the database
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
