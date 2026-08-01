from sqlalchemy.orm import Session
from models import BannedUser, Listable
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger("DCUBABOT")

async def process_ban_state(session: Session, context: ContextTypes.DEFAULT_TYPE) -> None:
    groups: list[Listable] = (
        session
        .query(Listable)
        .filter(Listable.validated == True)
        .all()
    )

    users_to_process: list[BannedUser] = (
        session
        .query(BannedUser)
        .filter(BannedUser.processed_lock == False)
        .all()
    )

    for group in groups:
        for user in users_to_process:
            try:
                await context.bot.ban_chat_member(group.chat_id, user.user_id)
                # logger.info(f"Processed ban user with id:\'{user.user_id}\' from group with id:\'{group.chat_id}\'")
            except Exception as e:
                # logger.error(f"Failed to process ban user with id:\'{user.user_id}\' from group with id:\'{group.chat_id}\', reason: {e}\n")
                pass

    for user in users_to_process:
        user.processed_lock = True
     
async def process_unban_state(user_id: int, session: Session, context: ContextTypes.DEFAULT_TYPE) -> None:
    groups: list[Listable] = (
        session
        .query(Listable)
        .filter(Listable.validated == True)
        .all()
    )

    for group in groups:
        try:
            await context.bot.unban_chat_member(group.chat_id, user_id)
            # logger.info(f"Processed unban of user with id:\'{user.user_id}\' from group with id:\'{group.chat_id}\'")
        except Exception as e:
            # logger.error(f"Failed to process unban user with id:\'{user.user_id}\' from group with id:\'{group.chat_id}\', reason: {e}\n")
            pass