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
from handlers.db import get_session
from models import ProcessedUpdate

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
    
    user_info = f"{user.id} ({user.username})" if user else None
    chat_info = f"{chat.id} ({chat.title})" if chat else None
    
    log_parts = ["Update received"]
    
    if user_info:
        log_parts.append(f"User: {user_info}")
    if chat_info:
        log_parts.append(f"Chat: {chat_info}")
        
    if update.channel_post:
        log_parts.append("Type: Channel Post")
        if update.channel_post.text:
            log_parts.append(f"Text: {update.channel_post.text}")
    elif update.edited_channel_post:
        log_parts.append("Type: Edited Channel Post")
    elif update.poll:
        log_parts.append(f"Type: Poll Update (id: {update.poll.id})")
    elif update.poll_answer:
        log_parts.append(f"Type: Poll Answer (poll_id: {update.poll_answer.poll_id})")
    elif update.my_chat_member:
        log_parts.append("Type: Bot Chat Member Status Update")
    elif update.chat_member:
        log_parts.append("Type: Chat Member Update")
    elif update.inline_query:
        log_parts.append(f"Type: Inline Query (query: {update.inline_query.query})")
    
    if update.message and update.message.text:
        log_parts.append(f"Message: {update.message.text}")
    elif update.callback_query:
        log_parts.append(f"Callback Query: {update.callback_query.data}")
        
    if not user_info and not chat_info and len(log_parts) == 1:
        log_parts.append("Type: Unknown/System Update")

    log_message = " | ".join(log_parts)
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
        
        # Idempotency check: Have we processed this update_id already?
        with get_session() as session:
            existing = session.query(ProcessedUpdate).filter_by(update_id=update.update_id).first()
            if existing:
                logging.getLogger("DCUBABOT").info(f"Skipping duplicate update_id {update.update_id}")
                return Response(status_code=200)
            
            # If not, mark as processed and commit immediately
            session.add(ProcessedUpdate(update_id=update.update_id))
            session.commit()

        # Await the processing SYNCHRONOUSLY before returning 200 OK
        # This prevents Cloud Run from throttling the CPU while the bot is doing work
        # TODO: If user traffic scales significantly and Telegram throws `RetryAfter` for
        # generic `send_message` calls, consider offloading processing or outbound
        # messages to Google Cloud Tasks / PubSub to decouple the HTTP response from the work.
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
