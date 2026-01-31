import telegram
import os

bot = telegram.Bot(os.environ["TELEGRAM_BOT_TOKEN"])

def webhook(request):
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        chat_id = update.message.chat.id

        bot.sendMessage(chat_id=chat_id, text=update.message.text)
    return True