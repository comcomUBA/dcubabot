#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Local imports
from models import *


def noitip(bot, update):
    with db_session:
        random_noitip = Noitip.select_random(1)[0].text
    update.message.reply_text(random_noitip, quote=False)


def asm(bot, update, args):
    if not args:
        update.message.reply_text("No me pasaste ninguna instrucción.", quote=False)
        return

    mnemonic = args[0].upper()
    with db_session:
        possibles = [i for i in list(AsmInstruction.select())
                     if levenshtein(mnemonic, i.mnemonic) < 2]
    if not possibles:
        update.message.reply_text("No pude encontrar esa instrucción.", quote=False)
    elif mnemonic in [i.mnemonic for i in possibles]:
        update.message.reply_text(getasminfo(possibles[0]), quote=False)
    else:
        response_text = ("No pude encontrar esa instrucción.\n"
                         "Quizás quisiste decir:")
        for instr in possibles:
            response_text += "\n" + getasminfo(instr)
        update.message.reply_text(response_text, quote=False)


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