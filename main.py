import telegram
import os
import logging
import html
import traceback
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
import uvicorn

from bot_logic import COMMANDS, button
from tg_ids import ROZEN_CHATID

async def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    logger = logging.getLogger("DCUBABOT")
    logger.error("Exception while handling an update:", exc_info=context.error)

    try:
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)
        
        message = f"⚠️ <b>Error en el bot:</b>\n<pre>{html.escape(tb_string)[:3800]}</pre>"
        await context.bot.send_message(chat_id=ROZEN_CHATID, text=message, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Failed to send error message to ROZEN: {e}")

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


async def post_init(application: Application):
    """Set the bot commands on startup."""
    from telegram import BotCommand
    commands = []
    for command_name, command_info in COMMANDS.items():
        if 'description' in command_info and command_info['description']:
            # Telegram commands must be lowercase and 1-32 chars
            commands.append(BotCommand(command_name.lower(), command_info['description'][:256]))
    
    try:
        await application.bot.set_my_commands(commands)
        logging.getLogger("DCUBABOT").info("Successfully set bot commands.")
    except Exception as e:
        logging.getLogger("DCUBABOT").error(f"Failed to set bot commands: {e}")

# Instancia global de la aplicación de Telegram
application = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).post_init(post_init).build()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup de la aplicación de Telegram al arrancar FastAPI
    await application.initialize()
    await application.start()
    
    webhook_url = os.environ["WEBHOOK_URL"]
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    url = f'{webhook_url.rstrip("/")}/{token}'
    await application.bot.set_webhook(url=url)
    
    yield
    
    # Shutdown
    await application.stop()
    await application.shutdown()

app = FastAPI(lifespan=lifespan)

@app.post("/{token}")
async def telegram_webhook(token: str, request: Request):
    if token != os.environ["TELEGRAM_BOT_TOKEN"]:
        return Response(status_code=403)
        
    try:
        data = await request.json()
        update = telegram.Update.de_json(data=data, bot=application.bot)
        # Await the processing SYNCHRONOUSLY before returning 200 OK
        # This prevents Cloud Run from throttling the CPU while the bot is doing work
        await application.process_update(update)
    except Exception as e:
        logging.error(f"Failed to process update: {e}")
        
    return Response(status_code=200)

def main():
    """Start the bot."""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s',
    )

    application.add_error_handler(error_handler)

    # Add the logging middleware handler with a high priority
    application.add_handler(MessageHandler(filters.ALL, log_update), group=-1)

    for command_name, command_info in COMMANDS.items():
        application.add_handler(CommandHandler(command_name, command_info['handler']))

    application.add_handler(CallbackQueryHandler(button))

    # Run the FastAPI app via uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
