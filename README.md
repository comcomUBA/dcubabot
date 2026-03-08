# dcubabot

La idea de este repositorio es migrar desde el viejo repositorio las funcionalidades que tiene el bot de forma estructurada, prolija y segura. Muy pronto traeremos bardearmarto, tranquilos.

Mientras seguimos la migración todos son libres de colaborar con pull requests.

Para probar el bot en acción en Telegram es necesario crear un archivo `tokenz.py` que asigne a la variable `token` el token del bot con el que se desea hacer las pruebas.

## Herramientas

### Desarrollo

- **Python 3.13**
- **[uv](https://docs.astral.sh/uv/)** – gestor de paquetes y entornos
- **[ruff](https://docs.astral.sh/ruff/)** (0.15.5) – linter y formatter
- **[mypy](https://mypy.readthedocs.io/)** (1.19.1) – verificador de tipos estáticos

El script `./check.sh` ejecuta ruff (linter + formatter) y mypy para validar el código.

### Dependencias principales

- [python-telegram-bot](https://python-telegram-bot.org/) – API de Telegram
- [Pony ORM](https://ponyorm.org/) – base de datos
- [icalevents](https://github.com/irgangla/icalevents) – calendarios iCal
- [pytz](https://pypi.org/project/pytz/) – zonas horarias
- [requests](https://requests.readthedocs.io/) – HTTP (ej. chequeo del campus)
- [RoboBrowser](https://github.com/jmcarp/robobrowser/) – scraping web
- [Werkzeug](https://werkzeug.palletsprojects.com/) – utilidades WSGI

## Instalación

### Con uv (recomendado)

Si no tenés uv instalado:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
# Instalar dependencias
uv sync

# Ejecutar el bot
uv run python dcubabot.py

# Chequear linter y formatter
./check.sh
```

### Con pip

```bash
pip3 install -r requirements.txt
```
