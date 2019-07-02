#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Local imports
from models import *


def noitip(update, context):
    with db_session:
        random_noitip = Noitip.select_random(1)[0].text
    msg = update.message.reply_text(random_noitip, quote=False)
    context.sent_messages.append(msg)


def asm(update, context):
    if not context.args:
        msg = update.message.reply_text("No me pasaste ninguna instrucción.", quote=False)
        context.sent_messages.append(msg)
        return

    mnemonic = " ".join(context.args).upper()
    with db_session:
        possibles = [i for i in list(AsmInstruction.select())
                     if levenshtein(mnemonic, i.mnemonic.upper()) < 2]
    if not possibles:
        msg = update.message.reply_text("No pude encontrar esa instrucción.", quote=False)
    else:
        instr_match = [i for i in possibles if i.mnemonic.upper() == mnemonic]
        if instr_match:
            response_text = ""
            response_text += "\n".join(getasminfo(i) for i in instr_match)
        else:
            response_text = ("No pude encontrar esa instrucción.\n"
                             "Quizás quisiste decir:\n")
            response_text += "\n".join(getasminfo(i) for i in possibles)
        msg =update.message.reply_text(response_text, quote=False)
    context.sent_messages.append(msg)


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
            tbl[i, j] = min(tbl[i, j - 1] + 1, tbl[i - 1, j] + 1, tbl[i - 1, j - 1] + cost)

    return tbl[i, j]


def getasminfo(instr):
    return '[%s] Descripción: %s.\nMás info: %s' % (
        instr.mnemonic,
        instr.summary,
        instr.url)
