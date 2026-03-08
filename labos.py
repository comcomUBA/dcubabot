from collections.abc import Generator, Iterator
from datetime import datetime, timedelta
from typing import Any

from icalevents import icaldownload, icalparser
from pytz import timezone

# (events, loaded, span, raw) - inicial: (None, epoch, 0, "") para forzar carga
CalendarEntry = tuple[list[Any] | None, datetime, timedelta, str]


def __calendar_url(calendar_id: str) -> str:
    return (
        "https://calendar.google.com/calendar/ical/"
        + str(calendar_id)
        + "%40group.calendar.google.com/public/basic.ics"
    )


urls = {
    "Labo 1": __calendar_url("s57pjfhll16pqpu456eonvb760"),
    "Labo 2": __calendar_url("bupjqrv2va0nb3bv3o1f1jqtc0"),
    "Labo 3 (Graduados)": __calendar_url("n3sd0tpdt0o5855evq8uvsi3vo"),
    "Labo 4": __calendar_url("4lbn08p17sv8s2pfqoophliag4"),
    "Labo 5": __calendar_url("fu35kvoh4i2looi4drjf17k1ts"),
    "Labo 6": __calendar_url("g3jdt9mmsrqllp7hqfotvttsck"),
    "Labo 7 (Turing)": __calendar_url("krs8uvil4o36kd3a3ad5qs57dg"),
}

tz = timezone("America/Buenos_Aires")

# (events, loaded, span, raw) - inicial vacío para forzar carga
calendars: dict[str, CalendarEntry] = {
    k: (None, datetime(2000, 1, 1, tzinfo=tz), timedelta(0), "") for k in urls
}


# Devuelve el momento actual con nuestra zona horaria.
def aware_now() -> datetime:
    return datetime.now(tz=tz)


# Decide si vale la pena o no recargar un calendario.
def should_reload(name: str) -> bool:
    calendar = calendars[name]
    return aware_now() - timedelta(hours=12) > calendar[1]


# Carga un calendario desde una url y lo guarda con la fecha de carga.
def load_calendar(name: str, retries: int = 3) -> CalendarEntry | None:
    url = urls[name]

    while retries > 0:
        try:
            now = aware_now()
            span = timedelta(weeks=4)
            calendar_raw = icaldownload.ICalDownload().data_from_url(url)
            events = icalparser.parse_events(
                calendar_raw,
                start=now - span,
                end=now + span,
            )
            calendars[name] = (events, now, span, calendar_raw)
            return calendars[name]
        except Exception:
            retries -= 1

    # Debería levantar una excepción?
    return None


# Dado el nombre de un calendario lo devuelve (y recarga si es necesario).
def get_calendar(name: str) -> CalendarEntry:
    if calendars[name][0] is None:
        retries = 100
    elif should_reload(name):
        retries = 3
    else:
        retries = 0

    # Si load_calendar falló fallbackeo
    return load_calendar(name, retries) or calendars[name]


# Repite el siguiente valor del generador, útil para ver si un generador está
# vacío sin romperlo.
def repeat_next(
    generator: Iterator[Any],
) -> Generator[Any]:
    empty = object()
    _next = next(generator, empty)

    if _next is empty:
        return

    yield _next
    yield _next
    yield from generator


# Este sería el API que exponemos.
# El datetime no puede ser naive.
def events_at(time: datetime) -> Iterator[str]:
    for name in calendars:
        calendar = get_calendar(name)

        # Vemos si podemos usar los eventos en caché o tenemos que parsear raw
        if calendar[1] - calendar[2] <= time <= calendar[1] + calendar[2] and calendar[0]:
            events_gen = (e for e in calendar[0] if e.start <= time <= e.end)
        else:
            events_gen = (e for e in icalparser.parse_events(calendar[3], start=time, end=time))
        events = repeat_next(events_gen)

        if next(events, None) is None:
            yield "[%s] No tiene nada reservado" % name

        for event in events:
            yield "[%s] %s" % (name, event.summary)


# Llamado periódicamente para forzar la actualización de los calendarios
async def update(context: object) -> None:
    for name in calendars:
        load_calendar(name)
