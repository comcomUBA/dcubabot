from datetime import datetime
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

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

def fetch_partidos():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    res = requests.get("https://www.cariverplate.com.ar/calendario-de-partidos", headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    partidos = []

    for el in soup.select(".d_calendario"):
        try:
            partidos.append(Partido.parse(el))
        except ValueError:
            pass
        
    return partidos

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

if __name__ == "__main__":
    print(es_local(datetime.today()))
