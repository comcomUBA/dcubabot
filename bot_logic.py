from orga2Utils import noitip, asm
from handlers.basic import start, help_command, estasvivo, colaborar
from handlers.info import campusvivo, flan, flanviejo, aulas, cuandovence, listarlabos
from handlers.admin import checodepers, checodeppers, sugerirNoticia, get_logs
from handlers.groups import listar, listaroptativa, listareci, listarotro, cubawiki, agregargrupo, agregaroptativa, agregarotros, agregareci, sugerirgrupo, sugeriroptativa, sugerireci, sugerirotro, actualizar_grupos, _update_groups
from handlers.callbacks import button
from handlers.crons import felizdia, actualizarRiver

COMMANDS = {
    'logs': {
        'handler': get_logs,
        'description': '(Admin) Revisa los últimos 10 errores en GCP.'
    },
    'listarlabos': {
        'handler': listarlabos,
        'description': 'Muestra las reservas de los laboratorios.'
    },
    'flan': {
        'handler': flan,
        'description': 'Muestra el plan de estudios de la carrera.'
    },
    'flanviejo': {
        'handler': flanviejo,
        'description': 'Muestra el plan de estudios viejo de la carrera.'
    },
    'aulas': {
        'handler': aulas,
        'description': 'Muestra el mapa de las aulas.'
    },
    'start': {
        'handler': start,
        'description': 'Inicia el bot.'
    },
    'help': {
        'handler': help_command,
        'description': 'Muestra este mensaje de ayuda.'
    },
    'estasvivo': {
        'handler': estasvivo,
        'description': 'Responde si el bot está funcionando.'
    },
    'listar': {
        'handler': listar,
        'description': 'Muestra los grupos de Telegram de materias obligatorias.'
    },
    'listaroptativa': {
        'handler': listaroptativa,
        'description': 'Muestra los grupos de Telegram de materias optativas.'
    },
    'listareci': {
        'handler': listareci,
        'description': 'Muestra los grupos de Telegram de las ECI.'
    },
    'listarotro': {
        'handler': listarotro,
        'description': 'Muestra otros grupos de Telegram.'
    },
    'cubawiki': {
        'handler': cubawiki,
        'description': 'Devuelve el link a la Cubawiki de la materia (si estás en el grupo de la materia).'
    },
    'agregargrupo': {
        'handler': agregargrupo,
        'description': 'Agrega el grupo actual a la lista de grupos de materias obligatorias.'
    },
    'agregaroptativa': {
        'handler': agregaroptativa,
        'description': 'Agrega el grupo actual a la lista de grupos de materias optativas.'
    },
    'agregareci': {
        'handler': agregareci,
        'description': 'Agrega el grupo actual a la lista de grupos de ECI.'
    },
    'agregarotros': {
        'handler': agregarotros,
        'description': 'Agrega el grupo actual a la lista de otros grupos.'
    },
    'sugerirnoticia': {
        'handler': sugerirNoticia,
        'description': 'Sugiere una noticia para el canal de noticias.'
    },
    'campusvivo': {
        'handler': campusvivo,
        'description': 'Verifica si el Campus Virtual está funcionando.'
    },
    'noitip': {
        'handler': noitip,
        'description': "Explica el meme 'No, it IP'."
    },
    'asm': {
        'handler': asm,
        'description': 'Explica el meme de Assembly.'
    },
    'checodepers': {
        'handler': checodepers,
        'description': 'Envía un mensaje a les codepers.'
    },
    'checodeppers': {
        'handler': checodeppers,
        'description': 'Alias para /checodepers.'
    },
    'cuandovence': {
        'handler': cuandovence,
        'description': 'Calcula cuándo vence la validez de los TPs de una materia.'
    },
    'colaborar': {
        'handler': colaborar,
        'description': 'Muestra el link al repositorio de Github del bot.'
    },
    'actualizar_grupos': {
        'handler': actualizar_grupos,
        'description': 'Actualiza los links de todos los grupos.'
    },
    'sugerirgrupo': {
        'handler': sugerirgrupo,
    },
    'sugeriroptativa': {
        'handler': sugeriroptativa,
    },
    'sugerireci': {
        'handler': sugerireci,
    },
    'sugerirotro': {
        'handler': sugerirotro,
    },
}
