import json

from datetime import datetime
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

@dataclass
class Concierto:
    titulo: str
    fecha: datetime.date
    
    @staticmethod
    def parse(evento):
        try:
            info = json.loads(evento.select("script")[0].text)[0]
            titulo = info["name"]
            fecha = info["startDate"].split("T")[0]
            
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
                    
            return Concierto(
                titulo,
                fecha,
            )
        except:
            return None
        
def fetch_conciertos():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    res = requests.get("https://www.songkick.com/venues/4514007-estadio-river-plate/calendar", headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    
    conciertos = []
    
    for el in soup.select(".microformat"):
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
