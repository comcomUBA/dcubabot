import telegram
import os
from flask import Flask, request

app = Flask(__name__)
bot = telegram.Bot(os.environ["TELEGRAM_BOT_TOKEN"])

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        chat_id = update.message.chat.id

        bot.sendMessage(chat_id=chat_id, text=update.message.text)
    return "OK"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
