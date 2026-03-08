"""Contexto personalizado para DCUBABOT con sent_messages."""

from typing import Any

from telegram.ext import CallbackContext, ContextTypes


class DCUBACallbackContext(CallbackContext[Any, Any, Any, Any]):
    """CallbackContext con sent_messages para DeletableCommandHandler."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.sent_messages: list[Any] = []


DCUBA_CONTEXT_TYPES = ContextTypes(context=DCUBACallbackContext)
