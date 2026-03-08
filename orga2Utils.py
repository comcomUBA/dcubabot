#!/usr/bin/python3

# Local imports
from telegram import Update

from context_types import DCUBACallbackContext
from models import AsmInstruction, Noitip, db_session


async def noitip(update: Update, context: DCUBACallbackContext) -> None:
    if update.message is None:
        return
    with db_session:
        tips = Noitip.select_random(1)
    if not tips:
        msg = await update.message.reply_text(
            "No hay tips cargados todavía.",
            do_quote=False,
        )
    else:
        msg = await update.message.reply_text(tips[0].text, do_quote=False)
    context.sent_messages.append(msg)


async def asm(update: Update, context: DCUBACallbackContext) -> None:
    if update.message is None:
        return
    if not context.args:
        msg = await update.message.reply_text(
            "No me pasaste ninguna instrucción.",
            do_quote=False,
        )
        context.sent_messages.append(msg)
        return

    mnemonic = " ".join(context.args).upper()
    with db_session:
        possibles = [
            i
            for i in list(AsmInstruction.select())
            if levenshtein(mnemonic, i.mnemonic.upper()) < 2
        ]
    if not possibles:
        msg = await update.message.reply_text(
            "No pude encontrar esa instrucción.",
            do_quote=False,
        )
    else:
        instr_match = [i for i in possibles if i.mnemonic.upper() == mnemonic]
        if instr_match:
            response_text = ""
            response_text += "\n".join(getasminfo(i) for i in instr_match)
        else:
            response_text = "No pude encontrar esa instrucción.\nQuizás quisiste decir:\n"
            response_text += "\n".join(getasminfo(i) for i in possibles)
        msg = await update.message.reply_text(response_text, do_quote=False)
    context.sent_messages.append(msg)


def levenshtein(string1: str, string2: str) -> int:
    len1 = len(string1) + 1
    len2 = len(string2) + 1

    tbl = {}
    for i in range(len1):
        tbl[i, 0] = i
    for j in range(len2):
        tbl[0, j] = j
    for i in range(1, len1):
        for j in range(1, len2):
            cost = 0 if string1[i - 1] == string2[j - 1] else 1
            tbl[i, j] = min(
                tbl[i, j - 1] + 1,
                tbl[i - 1, j] + 1,
                tbl[i - 1, j - 1] + cost,
            )

    return tbl[i, j]


def getasminfo(instr: AsmInstruction) -> str:
    return "[%s] Descripción: %s.\nMás info: %s" % (
        instr.mnemonic,
        instr.summary,
        instr.url,
    )
