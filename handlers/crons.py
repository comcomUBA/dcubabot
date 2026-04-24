import pytz
import datetime
import random
import logging
from telegram.ext import ContextTypes
from utils import river
from utils import conciertos
from tg_ids import DC_GROUP_CHATID, NOTICIAS_CHATID

logger = logging.getLogger("DCUBABOT")
bsasTz = pytz.timezone("America/Argentina/Buenos_Aires")

from handlers.db import get_session
from models import Lock

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
    today = datetime.date.today()
    lock_key = f"felizdia_{today.year}_{today.month}_{today.day}"
    
    with get_session() as session:
        existing = session.query(Lock).filter_by(key=lock_key).first()
        if existing:
            logger.info(f"felizdia already executed today ({today}). Skipping.")
            return
            
        new_lock = Lock(key=lock_key, expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=2))
        session.add(new_lock)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to acquire felizdia lock: {e}")
            return

    if random.uniform(0, 7) > 1:
        logger.info(f"felizdia skipped by random chance today ({today}).")
        return
        
    chat_id = DC_GROUP_CHATID
    await context.bot.send_message(chat_id=chat_id, text=felizdia_text(today))

async def actualizarPartidos(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.datetime.now(bsasTz)
    tomorrow = today + datetime.timedelta(days=1)

    if tomorrow.weekday() >= 5:
        return

    try:
        is_local, match = river.es_local(tomorrow)
        if not is_local:
            return
            
        weekdays = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        weekday_name = weekdays[tomorrow.weekday()]
        
        time_str = "hora a confirmar" if match.hora is None else match.hora.strftime("a las %H:%M")
        msg = f"Mañana {weekday_name} juega River, {time_str}\n(contra {match.equipo_visitante}, {match.copa})"
        await context.bot.send_message(chat_id=NOTICIAS_CHATID, text=msg)
    except Exception as e:
        logger.error(f"Error checking River matches: {e}")

async def actualizarConciertos(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.datetime.now(bsasTz)
    tomorrow = today + datetime.timedelta(days=1)

    if tomorrow.weekday() >= 5:
        return

    try:
        has_concert, concert = conciertos.hay_concierto(tomorrow)
        if not has_concert:
            return
            
        weekdays = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        weekday_name = weekdays[tomorrow.weekday()]
        
        msg = f"Mañana {weekday_name} hay un concierto en River\n{concert.titulo}"
        await context.bot.send_message(chat_id=NOTICIAS_CHATID, text=msg)
    except Exception as e:
        logger.error(f"Error checking concerts: {e}")

async def actualizarRiver(context: ContextTypes.DEFAULT_TYPE):
    await actualizarPartidos(context)
    await actualizarConciertos(context)
