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

    # Get webhook URL from environment.
    webhook_url_from_env = os.environ.get("WEBHOOK_URL")
    
    # Prepare the webhook_url parameter. It must be None if the env var is missing or empty.
    webhook_url_param = None
    if webhook_url_from_env: # This is only true if the string is not None and not empty.
        webhook_url_param = f'{webhook_url_from_env}/{os.environ["TELEGRAM_BOT_TOKEN"]}'

    # Start the Bot
    # If webhook_url_param is None, run_webhook will only start the webserver without setting a webhook.
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        #url_path=os.environ["TELEGRAM_BOT_TOKEN"],
        #webhook_url=webhook_url_param,
    )

if __name__ == "__main__":
    main()
