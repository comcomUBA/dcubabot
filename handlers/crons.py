import pytz
import datetime
import random
import logging
from telegram.ext import ContextTypes
import river
import conciertos
from tg_ids import DC_GROUP_CHATID, NOTICIAS_CHATID

logger = logging.getLogger("DCUBABOT")
bsasTz = pytz.timezone("America/Argentina/Buenos_Aires")

def felizdia_text(today):
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
             "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    dia = str(today.day)
    mes = int(today.month)

    if mes == 3 and today.day == 8:
        return "Hoy es 8 de Marzo"
    else:
        mes = meses[mes - 1]
        return "Feliz " + dia + " de " + mes

async def felizdia(context: ContextTypes.DEFAULT_TYPE):
    if random.uniform(0, 7) > 1:
        return
    today = datetime.date.today()
    chat_id = DC_GROUP_CHATID
    await context.bot.send_message(chat_id=chat_id, text=felizdia_text(today))

async def actualizarPartidos(context: ContextTypes.DEFAULT_TYPE):
    hoy = datetime.datetime.now(bsasTz)
    mañana = hoy + datetime.timedelta(days=1)
    try:
        local, partido = river.es_local(mañana)
        if not local:
            return
        horario = "hora a confirmar" if partido.hora is None else partido.hora.strftime("a las %H:%M")
        msg = f"Mañana juega River, {horario}\n(contra {partido.equipo_visitante}, {partido.copa})"
        await context.bot.send_message(chat_id=NOTICIAS_CHATID, text=msg)
    except Exception as e:
        logger.error(f"Error checking River matches: {e}")

async def actualizarConciertos(context: ContextTypes.DEFAULT_TYPE):
    hoy = datetime.datetime.now(bsasTz)
    mañana = hoy + datetime.timedelta(days=1)
    try:
        hay, concierto = conciertos.hay_concierto(mañana)
        if not hay:
            return
        msg = f"Mañana hay un concierto en River\n{concierto.titulo}"
        await context.bot.send_message(chat_id=NOTICIAS_CHATID, text=msg)
    except Exception as e:
        logger.error(f"Error checking concerts: {e}")

async def actualizarRiver(context: ContextTypes.DEFAULT_TYPE):
    await actualizarPartidos(context)
    await actualizarConciertos(context)
