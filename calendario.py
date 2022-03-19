from bs4 import BeautifulSoup
import requests
from itertools import chain
from dataclasses import dataclass
import re
from requests.exceptions import RequestException
from telegram import ParseMode

URL = 'https://exactas.uba.ar/calendario-academico/'


@dataclass
class ItemInformativo:
    titulo: str
    textos: list[str]


@dataclass
class InfoCalendario:
    finales: list[ItemInformativo]
    cursadas: dict[str, ItemInformativo]

    def final(self, mes):
        return next((
            item for item in self.finales
            if mes in item.titulo.lower()
        ), None)


def fechas_finales(soup):
    return [
        ItemInformativo(tag.text, list(tag.find_next_sibling().stripped_strings))
        for tag in chain(soup.find_all('h3'), soup.find_all('h4'))
        if tag.text.startswith('EXÁMENES')
    ]


def cursadas(soup):
    def coso(text):
        if 'VERANO' in text:
            return 'verano'
        if 'PRIMER' in text:
            return '1c'
        if 'SEGUNDO' in text:
            return '2c'

    return {
        coso(tag.text): ItemInformativo(tag.text, list(tag.find_next_sibling().stripped_strings))
        for tag in chain(soup.find_all('h2'), soup.find_all('h3'))
        # Ignoro bimestres y cursada de invierno
        if ('CUATRIMESTRE' in tag.text or 'VERANO' in tag.text) and 'INSCRIPCIÓN' not in tag.text
    }


def info_calendario_academico():
    # TODO: manejar excepciones
    # TODO: loggear errores
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, 'html.parser')
    return InfoCalendario(
        finales=fechas_finales(soup),
        cursadas=cursadas(soup))


def armar_respuesta(info):
    titulo = f'*{info.titulo}*\n'
    textos = [
        f'*{texto}*:' if 'fecha' in texto else f'- {texto}'
        for texto in info.textos
    ]
    fuente = f'\n*Para más información*: {URL}'
    return '\n'.join([titulo, *textos, fuente])


def final(update, context):
    # TODO: hacer el request en un job
    calendario = info_calendario_academico()

    meses = ['febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
             'septiembre', 'octubre', 'noviembre', 'diciembre']

    mes = "".join(context.args).lower().strip()
    if mes not in meses:
        ayuda = "Pasame un mes.\nEjemplo: /final febrero"
        msg = update.message.reply_text(ayuda, quote=False)
        context.sent_messages.append(msg)
        return

    info = calendario.final(mes)
    respuesta = armar_respuesta(info)
    msg = update.message.reply_text(
        respuesta, quote=False, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    context.sent_messages.append(msg)


def cuatrimestre(update, context):
    calendario = info_calendario_academico()

    cuatri = "".join(context.args).lower().strip()
    if cuatri not in calendario.cursadas.keys():
        ayuda = f"Pasame un cuatrimestre.\nOpciones: {', '.join(calendario.cursadas.keys())}"
        msg = update.message.reply_text(ayuda, quote=False)
        context.sent_messages.append(msg)
        return

    info = calendario.cursadas[cuatri]
    respuesta = armar_respuesta(info)
    msg = update.message.reply_text(
        respuesta, quote=False, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    context.sent_messages.append(msg)
