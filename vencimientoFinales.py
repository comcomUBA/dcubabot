import re
from abc import abstractmethod 

VERANO = "ver"
PCUAT = "1c"
SCUAT = "2c"
INVIERNO = "inv"

VERANOS = ["v", "ver", "verano"]
INVIERNOS = ["i", "inv", "invierno"]

PRIMEROS = VERANOS + [PCUAT]
SEGUNDOS = INVIERNOS + [SCUAT]

VENC_FEB_TXT = "Febrero/Marzo de "
EXT_ABR_TXT = "Abril de "
VENC_JUL_TXT = "Julio/Agosto de "
EXT_SEP_TXT = "Septiembre de "

## CARGAR EXCEPCIONES
#               año : cuatrimestres de validez (default 8)
EXCEPCIONES = { "2016": 12,
                "2017": 11,
                "2018": 10,
                "2019": 9}

class Cursada():
    @classmethod
    def nueva(self, cuatri, anio, validez):
        clase = next(sc for sc in self.__subclasses__() if sc.accepts(cuatri))
        return clase(cuatri, anio, validez)

    def __init__(self, cuatri, anio, validez):
        self.anio = int(anio)
        self.cuatri = cuatri
        self.validez = validez
        self.set_vencimientos()
    
    def fecha_aprobacion(self):
        return f"{self.cuatri} de {self.anio}"
    
class PrimerSemestre(Cursada):

    @classmethod
    def accepts(self, cuatri):
        return cuatri in PRIMEROS
    
    def set_vencimientos(self):
        self.anio_venc = self.anio + self.validez//2
        
        if self.validez % 2 == 0:
            self.fecha_vencimiento = VENC_FEB_TXT + str(self.anio_venc)
            self.fecha_extension = EXT_ABR_TXT + str(self.anio_venc)
        else:
            self.fecha_vencimiento = VENC_JUL_TXT + str(self.anio_venc)
            self.fecha_extension = EXT_SEP_TXT + str(self.anio_venc)

class SegundoSemestre(Cursada):

    @classmethod
    def accepts(self, cuatri):
        return cuatri in SEGUNDOS
    
    def set_vencimientos(self):
        self.anio_venc = self.anio + self.validez//2
        
        if self.validez % 2 == 0:
            self.fecha_vencimiento = VENC_JUL_TXT + str(self.anio_venc)
            self.fecha_extension = EXT_SEP_TXT + str(self.anio_venc)
        else:
            self.anio_venc += 1
            self.fecha_vencimiento = VENC_FEB_TXT + str(self.anio_venc)
            self.fecha_extension = EXT_ABR_TXT + str(self.anio_venc)

def parse_cuatri_y_anio(linea):
    # regex para parametros.
    r_entrada = r"^(?P<cuatri>[12]c|v(er(ano)?)?|i(nv(ierno)?)?)(?P<anio>20\d{2})$"
    entrada = re.search(r_entrada, linea)
    if not entrada:
        raise 

    cuatri = entrada.group("cuatri")
    anio = entrada.group("anio")

    return cuatri, anio

def calcular_vencimiento(cuatri, anio):

    # Unificar strings de verano/invierno
    cuatri = unificar_especiales(cuatri)

    txt_excepcion = ""
    cuatris_validez = 8

    if anio in EXCEPCIONES:
        cuatris_validez = EXCEPCIONES[anio]
        txt_excepcion = "\n\n*El vencimiento de tu cursada fue extendido por resolución del Consejo Directivo. Por esta razón la fecha que te muestra el bot es superior a los 8 cuatrimestres desde la cursada.*"
    
    cursada = Cursada.nueva(cuatri, anio, cuatris_validez)

    mje = armar_texto(cursada, txt_excepcion)

    return mje
    
def unificar_especiales(cuatri):
    if cuatri in VERANOS:
        cuatri = VERANO
    elif cuatri in INVIERNOS:
        cuatri = INVIERNO
    return cuatri

def armar_texto(cursada, txt_excepcion):
    mje = f"""Materia aprobada en {cursada.fecha_aprobacion()}.

Última fecha en la cual podés rendir: 
*{cursada.fecha_vencimiento}.*
    
Fecha complementaria: 
*{cursada.fecha_extension}* \*. 

(\*) Depende de la aprobación del CD para ese año. Consultar en el Depto. de Estudiantes (Pab. 2)."""
    mje += txt_excepcion

    return mje
