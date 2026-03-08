import json
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from robobrowser import RoboBrowser


@dataclass
class Concierto:
    titulo: str
    fecha: date

    @staticmethod
    def parse(evento: Any) -> "Concierto | None":
        try:
            info = json.loads(evento.select("script")[0].text)[0]
            titulo = info["name"]
            fecha = info["startDate"].split("T")[0]

            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

            return Concierto(
                titulo,
                fecha,
            )
        except Exception:
            return None


def fetch_conciertos() -> list[Concierto]:
    browser = RoboBrowser(parser="html.parser")

    browser.open("https://www.songkick.com/venues/4514007-estadio-river-plate/calendar")

    conciertos = []

    for el in browser.select(".microformat"):
        concierto = Concierto.parse(el)
        if concierto:
            conciertos.append(concierto)

    return conciertos


def hay_concierto(dt: datetime) -> tuple[bool, Concierto | None]:
    fecha = dt.date()

    conciertos = fetch_conciertos()

    for c in conciertos:
        if c.fecha != fecha:
            continue

        return True, c

    return False, None


if __name__ == "__main__":
    print(hay_concierto(datetime.today()))
