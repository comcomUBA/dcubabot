from pony.orm import *

db = Database()

class Command(db.Entity):
    name = Required(str)

db.bind('sqlite', 'commands.sqlite3', create_db=True)
db.generate_mapping(create_tables=True)

# TODO: Delete this
with db_session:
    Command.select().delete()
    Command(name="start")
    Command(name="help")
    Command(name="estasvivo")
    Command(name="listar")
    commit()