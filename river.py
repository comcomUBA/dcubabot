from datetime import datetime
import re

from dataclasses import dataclass

from robobrowser import RoboBrowser

# https://stackoverflow.com/questions/35226904/convert-spanish-date-in-string-format
# Si google responde con los meses en ingles entonces esto no es necesario
# Desde el codigo me responde con Dic en lugar de Dec como en el navegador
# Si no, hay que instalar el locale dependiendo de la distro

# sudo locale-gen es_ES.UTF-8; sudo update-locale         # Ubuntu
# https://wiki.archlinux.org/title/locale                 # Arch

import locale
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

RIVER = "River Plate"
UNSPECIFIED_TIMES = {"A confirmar", ""}


@dataclass
class Partido:
    equipo_local: str
    equipo_visitante: str
    copa: str
    fecha: datetime.date
    hora: datetime.time

    @property
    def es_local(self):
        return self.equipo_local == RIVER

    @staticmethod
    def parse(el):
        equipos = [e.strip() for e in el.select("b")[0].text.split("vs.")]
        line2 = el.select("p")[0].text
        copa, _, line2 = line2.partition(" • ")
        _fecha, _, line2 = line2.partition(" - ")
        _hora = line2

        if not RIVER in equipos:
            raise ValueError

        _dow, dmy = _fecha.split(" ")
        fecha = datetime.strptime(dmy, "%d/%m/%Y").date()

        hora = None
        if _hora not in UNSPECIFIED_TIMES:
            fmt = None
            if "." in _hora:
                fmt = "%H.%M"
            else:
                fmt = "%H"

            hora = datetime.strptime(_hora, fmt).time()

        return Partido(
            equipos[0],
            equipos[1],
            copa,
            fecha,
            hora,
        )
    
@dataclass
class Concierto:
    titulo: str
    fecha: datetime.date
    
    @staticmethod
    def parse(evento):
        # Esto es muy feo, si llegan a cambiar algo cagamos...
        dia = evento.select(".UIaQzd")[0].text
        mes = evento.select(".wsnHcb")[0].text
        titulo = evento.select(".YOGjf")[0].text
        lugar = evento.select(".zvDXNd")[0].text.lower()

        hoy = datetime.now().date() 
        anio = hoy.year # Asumimos que es de este año
        fecha = datetime.strptime(f"{dia} {mes} {anio}", "%d %b %Y").date()

        # Puede que nos de cualquier cosa la busqueda
        es_en_river = re.search(r'(Monumental|Alcorta 7597)', lugar, re.IGNORECASE)
        
        if not es_en_river:
            return None
        
        # Si el titulo tiene "vs" entonces es un partido de futbol (heuristica)
        # y ya lo cubre la otra funcion
        if "vs" in titulo.lower():
            return None
        
        return Concierto(
            titulo,
            fecha,
        )

def fetch_partidos():
    browser = RoboBrowser(parser="html.parser")
    browser.open("https://www.cariverplate.com.ar/calendario-de-partidos")

    partidos = []

    for el in browser.select(".d_calendario"):
        partidos.append(Partido.parse(el))
        
    return partidos

def fetch_conciertos():
    browser = RoboBrowser(parser="html.parser", user_agent='Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0')

    query = "Conciertos Av. Pres. Figueroa Alcorta 7597"
    browser.open(f"https://www.google.com/search?q={query}&ibp=htl;events")
    
    conciertos = []
    
    for el in browser.select(".gws-horizon-textlists__tl-lif"):
        concierto = Concierto.parse(el)
        if concierto:
            conciertos.append(concierto)

    return conciertos

def es_local(dt: datetime):
    fecha = dt.date()

    partidos = fetch_partidos()

    for p in partidos:
        if p.fecha != fecha:
            continue

        if not p.es_local:
            continue

        return True, p

    return False, None

def hay_concierto(dt: datetime):
    fecha = dt.date()

    conciertos = fetch_conciertos()

    for c in conciertos:
        if c.fecha != fecha:
            continue

        return True, c

    return False, None
    
if __name__ == "__main__":
    print(es_local(datetime.today()))
    print(hay_concierto(datetime.today()))
