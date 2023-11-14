import json

from datetime import datetime
from dataclasses import dataclass
from robobrowser import RoboBrowser

@dataclass
class Concierto:
    titulo: str
    fecha: datetime.date
    
    @staticmethod
    def parse(evento):
        info = json.loads(evento.select("script")[0].text)[0]
        titulo = info["name"]
        fecha = info["startDate"].split("T")[0]
        
        fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
                
        return Concierto(
            titulo,
            fecha,
        )
        
def fetch_conciertos():
    browser = RoboBrowser(parser="html.parser")

    browser.open("https://www.songkick.com/venues/4514007-estadio-river-plate/calendar")
    
    conciertos = []
    
    for el in browser.select(".microformat"):
        concierto = Concierto.parse(el)
        if concierto:
            conciertos.append(concierto)

    return conciertos

def hay_concierto(dt: datetime):
    fecha = dt.date()

    conciertos = fetch_conciertos()

    for c in conciertos:
        if c.fecha != fecha:
            continue

        return True, c

    return False, None
    
if __name__ == "__main__":
    print(hay_concierto(datetime.today()))
