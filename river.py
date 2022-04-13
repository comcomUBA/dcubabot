import datetime

from dataclasses import dataclass

from robobrowser import RoboBrowser

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
    def from_d_calendario(el):
        equipos = [e.strip() for e in el.select("b")[0].text.split("vs.")]
        line2 = el.select("p")[0].text
        copa, _, line2 = line2.partition(" • ")
        _fecha, _, line2 = line2.partition(" - ")
        _hora = line2

        if not RIVER in equipos:
            raise ValueError

        _dow, dmy = _fecha.split(" ")
        fecha = datetime.datetime.strptime(dmy, "%d/%m/%Y").date()

        hora = None
        if _hora not in UNSPECIFIED_TIMES:
            fmt = None
            if "." in _hora:
                fmt = "%H.%M"
            else:
                fmt = "%H"

            hora = datetime.datetime.strptime(_hora, fmt).time()

        return Partido(
            equipos[0],
            equipos[1],
            copa,
            fecha,
            hora,
        )


def fetch():
    browser = RoboBrowser(parser="html.parser")
    browser.open("https://www.cariverplate.com.ar/calendario-de-partidos")

    res = []

    for el in browser.select(".d_calendario"):
        res.append(Partido.from_d_calendario(el))

    return res


def es_local(dt: datetime.datetime):
    fecha = dt.date()

    partidos = fetch()

    for p in partidos:
        if p.fecha == fecha:
            continue

        if not p.es_local:
            continue

        return True, p

    return False, None


if __name__ == "__main__":
    partidos = fetch()

    print(es_local(datetime.datetime.today()))
