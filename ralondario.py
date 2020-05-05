#!/usr/bin/python3
# -*- coding: utf-8 -*-

from calendarios import proximos_eventos

ID = "e1qrrpdi9d2ki9ruibp9gno484"

def formatear_nombre(txt, descripcion):
  if len(descripcion) > 0:
    pass # TODO: Mejorar el texto en base los tags en la descripción
  return txt

def formatear_hora(txt):
  return txt

def formatear_fecha(txt, monospace=False):
  if (monospace):
    if txt[8] == "0":
      txt = txt[:8] + " " + txt[9:]
    if txt[5] == "0":
      txt = txt[:5] + txt[6] + " " + txt[7:]
    return txt[8:10] + "/" + txt[5:7]
  return str(int(txt[8:10])) + "/" + str(int(txt[5:7]))

def proximos_eventos_ralondario(dias=7, monospace=False):
  mensaje = "Pŕoximos eventos:"
  eventos = []
  for evento in proximos_eventos(ID, 10, dias):
    nombre = formatear_nombre(evento.summary, evento.description)
    inicio = str(evento.start)
    fecha = formatear_fecha(inicio[:10], monospace)
    hora = None
    texto = nombre
    if len(inicio) > 20:
      hora = formatear_hora(inicio[11:16])
      texto += " a las " + hora
    if len(evento.location) > 0:
      lugar = evento.location
      texto += " en " + lugar
    eventos.append({"fecha":fecha,"texto":texto})
  fecha = ""
  if (monospace):
    for evento in eventos:
      if evento["fecha"] != fecha:
        fecha = evento["fecha"]
        mensaje += "\n" + fecha + ": " + evento["texto"]
      else:
        mensaje += "\n       " + evento["texto"]
  else:
    for evento in eventos:
      if evento["fecha"] != fecha:
        fecha = evento["fecha"]
        mensaje += "\n[[ " + fecha + " ]]"
      mensaje += "\n * " + evento["texto"]
  return mensaje
