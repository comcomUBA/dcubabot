import logging
from functools import wraps

def log_command(func):
    """A decorator to log command usage."""
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        logger = logging.getLogger("DCUBABOT")
        command_name = func.__name__
        user = update.effective_user
        chat = update.effective_chat
        logger.info(f"Command '{command_name}' triggered by user {user.id} ({user.username}) in chat {chat.id} ({chat.title})")
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in command '{command_name}': {e}", exc_info=True)
            raise
    return wrapper
