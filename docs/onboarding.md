# Guía para empezar a desarrollar

¡Te damos la bienvenida al desarrollo del DC-UBA Bot! Esta guía te va a ayudar a entender cómo está estructurado el código, cómo interactuar con la base de datos y cómo agregar nuevas funcionalidades de manera fácil.

## 🧭 Tour por el Código (Arquitectura)

El código está dividido en varias carpetas y archivos clave para mantener todo ordenado:

- `main.py`: Es el punto de entrada principal. Inicializa el bot, levanta el servidor web con FastAPI (para recibir los Webhooks de Telegram) y registra todos los comandos.
- `bot_logic.py`: Acá vive el diccionario `COMMANDS` que funciona como el registro central de todos los comandos que el bot entiende. Todo comando nuevo DEBE registrarse acá.
- `models.py`: Define todas las tablas de la base de datos (usando SQLAlchemy). Si necesitás guardar un dato nuevo, lo agregás acá como una clase.
- `cron.py`: El script que ejecuta tareas programadas (como `/felizdia`). Funciona de manera independiente al servidor de FastAPI.
- `handlers/`: Contiene la lógica de respuesta para cada comando. Está dividido en categorías:
  - `admin.py`: Comandos de administración.
  - `basic.py`: Comandos básicos como `/start`, `/help`.
  - `groups.py`: Toda la lógica de listar y sugerir grupos de materias, optativas, etc.
  - `info.py`: Consultas generales (campus, aulas, vencimientos, menús, etc.).
  - `callbacks.py`: Maneja los botones interactivos en los mensajes.
- `utils/`: Archivos con lógica de negocio y helpers que *no son comandos directos* (por ejemplo: el validador del campus, el algoritmo de vencimientos, conectores con APIs externas).

---

## ⚙️ Conceptos Clave y Funcionalidades Especiales

### 1. Botones y Callbacks en Telegram
Cuando el bot manda un mensaje con botones (teclados integrados o "Inline Keyboards"), cada botón tiene asociado un texto visible y un "callback data" (un string invisible).
- **Cómo funcionan:** Al tocar el botón, Telegram envía un evento especial llamado `CallbackQuery` en lugar de un mensaje normal.
- **Dónde se maneja:** Todos los botones del bot se procesan en la función `button` de `handlers/callbacks.py`.
- **Estructura de datos:** Para saber qué hacer, el "callback data" del botón suele armarse separando información con barras verticales (`|`). Por ejemplo: `"MoverGrupo|15|Select"`. Luego, en `handlers/callbacks.py` se hace un `.split("|")` para saber la acción y a qué elemento aplica.

### 2. Tareas Programadas (El Cronjob)
Hay procesos que el bot no hace en respuesta a un usuario, sino que corren periódicamente (por ejemplo, chequear si es el "feliz día" o si juega River).
- **El archivo `cron.py`:** A diferencia de `main.py` (que se queda escuchando mensajes todo el tiempo), `cron.py` se ejecuta una sola vez de principio a fin y luego se apaga.
- **Cómo funciona en producción:** Google Cloud Scheduler lo ejecuta periódicamente (generalmente cada unas horas o una vez al día) como un "Cloud Run Job".
- **Manejo de Errores y Diagnóstico:** El script está diseñado para no fallar silenciosamente ni interrumpirse. Cada tarea (`felizdia`, `actualizarRiver`, etc.) está envuelta en un bloque `try/except`. Si una falla, captura el error completo y se lo envía por mensaje privado a los administradores, para luego continuar con la siguiente tarea. Al finalizar todo, calcula cuánta memoria RAM consumió el proceso y envía un reporte de diagnóstico también por privado.
- **Limpieza:** Además de mandar avisos, el cron ejecuta limpiezas internas (como borrar mensajes viejos procesados en la base de datos).

### 3. La Lógica de River Plate (y conciertos)
Como Ciudad Universitaria está al lado de la cancha de River, saber si hay partido o recital es vital para los estudiantes (por el colapso del transporte y accesos).
- **El comando/aviso:** La función `actualizarRiver` en `handlers/crons.py` se corre automáticamente dentro del cronjob.
- **Cómo sabe si hay partido:** En `utils/river.py` se realiza un *web scraping* (usando `BeautifulSoup`) a la página web oficial de River Plate para leer el calendario. Si River juega de local, manda el aviso al canal de noticias. Hace lo mismo para los conciertos importando lógica desde `utils/conciertos.py`.

### 4. Actualización de Enlaces de Grupos (`_update_groups`)
Los enlaces de invitación a los grupos de Telegram a veces caducan, los grupos migran a supergrupos, o se vuelven inaccesibles. Para evitar tener links rotos, el bot hace un mantenimiento automático.
- **La tarea:** Dentro de `cron.py` se ejecuta `_update_groups` (que vive en `handlers/groups.py`).
- **El mecanismo:** Para cada grupo registrado y validado en la base de datos, el bot usa la API de Telegram para intentar regenerar o exportar el link de invitación actual (`update_group_url`).
- **Si falla:** Si la API devuelve que el bot ya no tiene permisos o el grupo fue borrado, lo desvalida en la base de datos y manda un aviso fúnebre ("El grupo murió 💀") al canal de los administradores.

---

## 🚀 Cómo agregar un comando nuevo

Agregar un comando es un proceso muy simple y requiere solo dos pasos:

### 1. Crear la función del comando (Handler)

Los comandos suelen ir en la carpeta `handlers/`. Si vas a hacer un comando informativo, lo ideal es ponerlo en `handlers/info.py`. 

Una función de comando siempre recibe `update` y `context`, y es `async`:

```python
# En handlers/info.py
from telegram import Update
from telegram.ext import ContextTypes

async def micomando(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Descripción breve de lo que hace el comando."""
    # Lógica del comando...
    await update.message.reply_text("¡Hola! Este es mi nuevo comando.")
```

### 2. Registrar el comando en `bot_logic.py`

Abrí el archivo `bot_logic.py`. Primero importá tu función:

```python
from handlers.info import micomando
```

Y después, agregalo al diccionario `COMMANDS`:

```python
COMMANDS = {
    # ... otros comandos ...
    'micomando': {
        'handler': micomando,
        'description': 'Dice hola en mi nuevo comando'
    },
}
```

¡Listo! El `main.py` se va a encargar automáticamente de registrarlo en Telegram usando la librería `python-telegram-bot`.

---

## 💾 La Base de Datos (SQLAlchemy)

El bot usa **PostgreSQL** y nos comunicamos a través de la librería `SQLAlchemy`.

### El Administrador de Sesiones (`get_session`)

Para no lidiar con abrir y cerrar la conexión manualmente, tenemos un "Context Manager" en `handlers/db.py`. **Siempre** que necesites leer o escribir en la base de datos, tenés que usar la función `get_session`:

```python
from handlers.db import get_session
from models import Listable # El modelo/tabla que quieras usar

# Leer datos:
with get_session() as session:
    grupos = session.query(Listable).filter_by(validated=True).all()
    for grupo in grupos:
        print(grupo.name)

# Escribir / Modificar datos:
with get_session() as session:
    nuevo_grupo = Listable(name="Álgebra 1", url="https://t.me/...", validated=False)
    session.add(nuevo_grupo)
    # ¡No hace falta hacer session.commit()!
    # El `with` se encarga de guardar automáticamente cuando termina el bloque.
```

### Modelos y Tablas (`models.py`)

Si mirás en `models.py`, vas a ver clases que heredan de `Base`. Cada clase es una tabla:
- `SentMessage`: Guarda qué mensajes mandó el bot para después poder borrarlos (usando el `DeletableCommandHandler`).
- `Listable`: Es la tabla principal para los grupos, optativas, ECIs, etc. Usa polimorfismo para guardar todo en la misma tabla pero diferenciar los tipos.

**Si necesitás guardar datos nuevos**:
Simplemente abrí `models.py`, creá tu clase nueva heredando de `Base`, y la próxima vez que el bot levante, SQLAlchemy se encarga de crear la tabla por vos gracias a la función `init_db()`.

---

## 🧹 Evitando el Spam (`DeletableCommandHandler`)

Para mantener los grupos de Telegram limpios y evitar que la respuesta a comandos muy usados (como `/aulas` o `/campusvivo`) ocupe toda la pantalla, el bot cuenta con una funcionalidad especial llamada `DeletableCommandHandler` (ubicada en `utils/deletablecommandhandler.py`).

- **¿Qué hace?** Si alguien manda un comando y el bot responde, la próxima vez que alguien mande *ese mismo comando* en el grupo (dentro de un margen de 24 horas), el bot **borra automáticamente su respuesta anterior** antes de enviar la nueva.
- **¿Cómo funciona por detrás?** Cada vez que el bot manda un mensaje a través de este *handler*, guarda el ID de ese mensaje en la base de datos (en la tabla `SentMessage`). Cuando vuelve a procesar el mismo comando, busca los mensajes anteriores, le pide a la API de Telegram que los elimine y borra los registros de la DB.

---

## 🛠️ Herramientas Auxiliares (`utils/`)

El bot esconde lógica muy interesante que no está directamente ligada a Telegram. Estas lógicas se modularizan en la carpeta `utils/`. Algunos ejemplos clave:

- `vencimientoFinales.py`: Es un algoritmo súper robusto (`calcular_vencimiento`) que, dado un año y un cuatrimestre, sabe exactamente cuándo se vence la materia teniendo en cuenta las **prórrogas históricas** y los años donde las fechas fueron excepcionales por la pandemia (basándose en las resoluciones oficiales).
- `labos.py`: Es un script que lee y "parsea" archivos de calendario `.ics` (iCal) para saber a qué hora están reservados y ocupados los laboratorios de la facultad. *(Nota: Actualmente esta funcionalidad está medio deprecada porque los links a los calendarios viejos dejaron de funcionar. ¡Buscamos a alguien que averigüe cómo acceder a los nuevos!)*
- `orga2Utils.py`: Tiene lógica para analizar instrucciones de lenguaje ensamblador (Assembler x86) y para calcular la distancia de *Levenshtein*, lo cual permite adivinar qué quiso escribir el usuario si se equivoca en un comando.

---

## 👮‍♂️ Permisos y Comandos de Administración

Algunas funciones del bot no pueden ser ejecutadas por cualquier usuario (por ejemplo, mandar mensajes en nombre del bot, recategorizar grupos o pedir los registros de errores).

- **¿Dónde están?** Estos comandos están definidos en `handlers/admin.py`.
- **¿Cómo saben que soy administrador?** Dentro del código vas a ver listas como `admin_ids = [ROZEN_CHATID, DGARRO_CHATID]`. Estos identificadores (que provienen del archivo `tg_ids.py`) son los IDs numéricos de Telegram de los administradores. Si un usuario que no está en la lista intenta ejecutar el comando, el bot lo ignora y registra una advertencia en los logs.
- **Visualizar Errores (`/logs`):** Gracias a su despliegue en Google Cloud Run, el bot puede consultar sus propios errores. Cuando un administrador usa este comando, el bot se conecta usando la librería `google-cloud-logging`, filtra los errores recientes y se los envía por privado.
