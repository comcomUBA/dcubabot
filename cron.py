import asyncio
import os
import logging
from telegram.ext import Application
from bot_logic import _update_groups

def main():
    """Runs the update_groups command."""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s',
    )

    application = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()
    
    async def run_update():
        await _update_groups(application)

    asyncio.run(run_update())

if __name__ == "__main__":
    main()
