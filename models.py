#!/usr/bin/python3

from __future__ import annotations

import datetime

from pony.orm import (
    Database,
    Optional,
    Required,
    commit,
    db_session,
)

__all__ = [
    "ECI",
    "AsmInstruction",
    "Command",
    "File",
    "Grupo",
    "GrupoOptativa",
    "GrupoOtros",
    "Listable",
    "Noitip",
    "Noticia",
    "Obligatoria",
    "Optativa",
    "Otro",
    "SentMessage",
    "commit",
    "db",
    "db_session",
    "init_db",
]

db = Database()
DbEntity = db.Entity


class Command(DbEntity):  # type: ignore[misc, valid-type]
    name = Required(str)
    description = Optional(str)
    enabled = Required(bool, default=True)


class SentMessage(DbEntity):  # type: ignore[misc, valid-type]
    command = Required(str)
    chat_id = Required(int, size=64)
    message_id = Required(int, size=64)
    timestamp = Required(datetime.datetime, default=datetime.datetime.utcnow)


class Listable(DbEntity):  # type: ignore[misc, valid-type]
    name = Required(str)
    url = Required(str)
    chat_id = Optional(str)
    validated = Required(bool, default=False)


class Obligatoria(Listable):
    cubawiki_url = Optional(str)


class Optativa(Listable):
    pass


class ECI(Listable):
    pass


class Otro(Listable):
    pass


class Grupo(Listable):
    pass


class GrupoOptativa(Listable):
    pass


class GrupoOtros(Listable):
    pass


# TODO: Subclasificar con validable
class Noticia(DbEntity):  # type: ignore[misc, valid-type]
    text = Required(str)
    date = Required(datetime.date, default=datetime.date.today())
    validado = Required(bool, default=True)


class Noitip(DbEntity):  # type: ignore[misc, valid-type]
    text = Required(str)


class AsmInstruction(DbEntity):  # type: ignore[misc, valid-type]
    mnemonic = Required(str)
    summary = Required(str)
    url = Required(str)


class File(DbEntity):  # type: ignore[misc, valid-type]
    path = Required(str)
    file_id = Required(str)


def init_db(path: str) -> None:
    db.bind("sqlite", path, create_db=True)
    db.generate_mapping(create_tables=True)
