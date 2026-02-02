#!/usr/bin/python3
# -*- coding: utf-8 -*-

from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
# Local imports
import models

@contextmanager
def get_session():
    """Provide a transactional scope around a series of operations."""
    if models.Session is None:
        models.init_db()
    session = models.Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


async def noitip(update, context):
    with get_session() as session:
        random_noitip = session.query(models.Noitip).order_by(func.random()).first().text
    msg = await update.message.reply_text(random_noitip)
    context.chat_data.setdefault('sent_messages', []).append(msg)


async def asm(update, context):
    if not context.args:
        msg = await update.message.reply_text(
            "No me pasaste ninguna instrucción.")
        context.chat_data.setdefault('sent_messages', []).append(msg)
        return

    mnemonic = " ".join(context.args).upper()
    response_text = ""
    with get_session() as session:
        all_instructions = session.query(models.AsmInstruction).all()
        possibles = [i for i in all_instructions
                     if levenshtein(mnemonic, i.mnemonic.upper()) < 2]
        if not possibles:
            response_text = "No pude encontrar esa instrucción."
        else:
            instr_match = [i for i in possibles if i.mnemonic.upper() == mnemonic]
            if instr_match:
                response_text = "\n".join(getasminfo(i) for i in instr_match)
            else:
                response_text = ("No pude encontrar esa instrucción.\n"
                                 "Quizás quisiste decir:\n")
                response_text += "\n".join(getasminfo(i) for i in possibles)
    msg = await update.message.reply_text(response_text)
    context.chat_data.setdefault('sent_messages', []).append(msg)


def levenshtein(string1, string2):
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
            tbl[i, j] = min(tbl[i, j - 1] + 1, tbl[i - 1, j] +
                            1, tbl[i - 1, j - 1] + cost)

    return tbl[i, j]


def getasminfo(instr):
    return '[%s] Descripción: %s.\nMás info: %s' % (
        instr.mnemonic,
        instr.summary,
        instr.url)
