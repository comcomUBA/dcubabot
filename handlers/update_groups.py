#!/usr/bin/python3
from asyncio import sleep

from pony.orm import db_session
from telegram import Update

from context_types import DCUBACallbackContext
from models import Listable
from tg_ids import DC_GROUP_CHATID


async def update_group_url(
    context: DCUBACallbackContext,
    chat_id: str,
) -> tuple[str | None, str | None, bool]:
    try:
        url = await context.bot.export_chat_invite_link(chat_id=chat_id)
    except Exception:  # TODO: filter excepts
        return None, None, False  # too GO-like huh?
    else:
        return chat_id, url, True  # too GO-like huh?


async def update_groups(context: DCUBACallbackContext) -> None:
    with db_session:
        chats = [
            (item.id, item.chat_id, item.name)
            for item in list(Listable.select(lambda item: item.validated))
        ]
    for item_id, chat_id, name in chats:
        if chat_id is None:
            continue
        _chat_id, url, validated = await update_group_url(context, chat_id)
        await sleep(1)
        if not validated:
            with db_session:
                group = Listable.get(id=item_id)
                if group is not None:
                    group.validated = False
            await context.bot.send_message(
                chat_id=DC_GROUP_CHATID,
                text=f"El grupo {name} murió 💀",
            )
        else:
            with db_session:
                group = Listable.get(id=item_id)
                if group is not None:
                    group.url = url


async def actualizar_grupos(update: Update, context: DCUBACallbackContext) -> None:
    await update_groups(context)
