from pony.orm import *

db = Database()

class Command(db.Entity):
    name = Required(str)
    description = Optional(str)

db.bind('sqlite', 'commands.sqlite3', create_db=True)
db.generate_mapping(create_tables=True)

# TODO: Delete this
with db_session:
    Command.select().delete()
    Command(name="start")
    Command(name="help", description="Muesta este mensaje horrible")
    Command(name="estasvivo", description="Responde un mensaje corto para ver si el bot esta al día y activo")
    Command(name="listar", description="Muestra todos los grupos de materias obligatorias conocidos por el bot")
    commit()