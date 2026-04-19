from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from campus import is_campus_up
from vencimientoFinales import calcular_vencimiento, parse_cuatri_y_anio
from handlers.media import responder_imagen, responder_documento

async def campusvivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Bancá que me fijo...")
    campus_response_text = is_campus_up()
    await context.bot.edit_message_text(chat_id=msg.chat_id,
                                message_id=msg.message_id,
                                text=msg.text + "\n" + campus_response_text)

async def flan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await responder_imagen(update, context, 'files/Plandeestudios-23.png')

async def flanviejo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await responder_imagen(update, context, 'files/Plandeestudios-93.png')

async def aulas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await responder_documento(update, context, 'files/0I-aulas.pdf')

async def cuandovence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ejemplo = "\nCuatris: 1c, 2c, i, inv, invierno, v, ver, verano.\nEjemplo: /cuandovence verano2010"
    if not context.args:
        ayuda = "Pasame cuatri y año en que aprobaste los TPs." + ejemplo
        await update.message.reply_text(ayuda)
        return
    try:
        linea_entrada = "".join(context.args).lower()
        cuatri, anio = parse_cuatri_y_anio(linea_entrada)
    except Exception:
        await update.message.reply_text(
            "¿Me pasás las cosas bien? Es cuatri+año." + ejemplo)
        return

    vencimiento = calcular_vencimiento(cuatri, anio)
    await update.message.reply_text(
        vencimiento, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

async def listarlabos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Che, creo que la info de los laboratorios caducó y no tengo esta data. Si tenés alguna fuente de información actualizada o calendarios nuevos, pasásela a @Rozen para que lo pueda agregar."
    await update.message.reply_text(text=msg)
