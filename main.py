import telegram
import os
from flask import Flask, request
from bot_logic import handle_command
from models import init_db

app = Flask(__name__)
bot = telegram.Bot(os.environ["TELEGRAM_BOT_TOKEN"])
init_db()

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    if update.message and update.message.text and update.message.text.startswith('/'):
        handle_command(update, bot)
    else:
        # Handle non-command messages if necessary
        pass
    return "OK"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
