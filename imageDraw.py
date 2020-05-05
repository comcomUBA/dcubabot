#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Requiere tener imageMagick instalado
  # $ sudo apt install imagemagick

import os

def abrir_imagen(ruta_imagen):
  return ImagenDibujable(ruta_imagen)

def generar_color(color):
  alfa = 1
  if len(color) == 4:
    alfa = color[3]
  return "\"rgba(" + \
    str(color[0]) + ", " + \
    str(color[1]) + ", " + \
    str(color[2]) + ", " + \
    str(alfa) + ")\""

class ImagenDibujable:
  def __init__(self, ruta):
    self.ruta = ruta
    self.dibujos = []
    self.defaults = {
      "font":"helvetica",
      "pointsize":"20",
      "fill":"\"rgba(0, 0, 0, 1)\""
    }

  def set_fuente(self, font):
    this.defaults["font"] = font

  def set_tamanio(self, size):
    this.defaults["pointsize"] = str(size)

  def set_color(self, color):
    this.defaults["fill"] = generar_color(color)

  def escribir(self, texto, posicion, color=None, tamanio=None, fuente=None):
    nuevo_dibujo = "-font "
    if (fuente is None):
      nuevo_dibujo += self.defaults["font"]
    else:
      nuevo_dibujo += fuente
    nuevo_dibujo += " -pointsize "
    if (tamanio is None):
      nuevo_dibujo += self.defaults["pointsize"]
    else:
      nuevo_dibujo += str(tamanio)
    nuevo_dibujo += " -fill "
    if (color is None):
      nuevo_dibujo += self.defaults["fill"]
    else:
      nuevo_dibujo += generar_color(color)
    nuevo_dibujo += " -draw \"text " + \
      str(posicion[0]) + "," + str(posicion[1]) + \
      "'" + texto + "'\" "
    self.dibujos.append(nuevo_dibujo)

  def guardar_imagen(self, ruta):
    comando = "convert " + self.ruta + " "
    for dibujo in self.dibujos:
      comando += dibujo
    comando += ruta
    os.system(comando)
