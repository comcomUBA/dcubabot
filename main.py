import telegram
import os
from telegram.ext import Updater, CommandHandler
from bot_logic import COMMANDS
from models import init_db

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.environ["TELEGRAM_BOT_TOKEN"])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    for command_name, command_handler in COMMANDS.items():
        dispatcher.add_handler(CommandHandler(command_name, command_handler))

    # Initialize the database
    init_db()

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(os.environ.get('PORT', 8080)),
                          url_path=os.environ["TELEGRAM_BOT_TOKEN"])
    #updater.bot.setWebhook('https://' + os.environ['HEROKU_APP_NAME'] + '.herokuapp.com/' + os.environ["TELEGRAM_BOT_TOKEN"])

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == "__main__":
    main()
