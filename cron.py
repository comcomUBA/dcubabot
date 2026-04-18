import asyncio
import os
import logging
import traceback
import resource
from telegram.ext import Application
from tg_ids import ROZEN_CHATID
from bot_logic import _update_groups, felizdia, actualizarRiver

def main():
    """Runs the update_groups command."""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s',
    )

    application = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()
    
    async def run_update():
        try:
            await application.bot.send_message(chat_id=ROZEN_CHATID, text="Arrancando cron job...")
        except Exception:
            pass

        try:
            await felizdia(application)
        except Exception as e:
            error_msg = f"Error en felizdia:\n{traceback.format_exc()}"
            await application.bot.send_message(chat_id=ROZEN_CHATID, text=error_msg[:4000])

        try:
            await actualizarRiver(application)
        except Exception as e:
            error_msg = f"Error en actualizarRiver:\n{traceback.format_exc()}"
            await application.bot.send_message(chat_id=ROZEN_CHATID, text=error_msg[:4000])

        try:
            await _update_groups(application)
        except Exception as e:
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
        except Exception as e:
            logging.error(f"Failed to send memory report: {e}")

    asyncio.run(run_update())

if __name__ == "__main__":
    main()
