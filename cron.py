import asyncio
import os
import logging
import traceback
import resource
import datetime
from telegram.ext import Application
from tg_ids import ROZEN_CHATID
from handlers.groups import _update_groups
from handlers.crons import felizdia, actualizarRiver
from handlers.db import get_session
from models import ProcessedUpdate

def main():
    """Runs the update_groups command."""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s',
    )

    application = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()
    
    async def run_update():
        try:
            # Clean up old processed updates (older than 48h) to save DB space
            with get_session() as session:
                forty_eight_hours_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=48)
                deleted = session.query(ProcessedUpdate).filter(ProcessedUpdate.timestamp < forty_eight_hours_ago).delete()
                logging.info(f"Cleaned up {deleted} old processed updates from DB")
        except Exception as e:
            logging.error(f"Error cleaning up processed updates: {e}", exc_info=True)

        try:
            await felizdia(application)
        except Exception:
            error_msg = f"Error en felizdia:\n{traceback.format_exc()}"
            await application.bot.send_message(chat_id=ROZEN_CHATID, text=error_msg[:4000])

        try:
            await actualizarRiver(application)
        except Exception:
            error_msg = f"Error en actualizarRiver:\n{traceback.format_exc()}"
            await application.bot.send_message(chat_id=ROZEN_CHATID, text=error_msg[:4000])

        try:
            await _update_groups(application)
        except Exception:
            error_msg = f"Error en update_groups:\n{traceback.format_exc()}"
            await application.bot.send_message(chat_id=ROZEN_CHATID, text=error_msg[:4000])

        # Reporte final con uso de RAM de este contenedor
        try:
            memory_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            memory_mb = memory_kb / 1024.0
            await application.bot.send_message(
                chat_id=ROZEN_CHATID, 
                text=f"Cron job finalizado. RAM máxima utilizada: {memory_mb:.2f} MB"
            )
        except Exception:
            logging.error(f"Failed to send memory report: {e}")

    asyncio.run(run_update())

if __name__ == "__main__":
    main()
