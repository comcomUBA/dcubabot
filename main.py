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

    # Get webhook URL from environment, but don't fail if it's not there
    webhook_url = os.environ.get("WEBHOOK_URL")
    if webhook_url:
        webhook_url = f'{webhook_url}/{os.environ["TELEGRAM_BOT_TOKEN"]}'


    # Start the Bot
    # On the first deploy, webhook_url will be None, and the bot will just start listening.
    # On the second deploy (after the workflow updates the env var), it will be set correctly.
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        url_path=os.environ["TELEGRAM_BOT_TOKEN"],
        webhook_url=webhook_url,
    )

if __name__ == "__main__":
    main()
