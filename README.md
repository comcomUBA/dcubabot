# dcubabot

La idea de este repositorio es migrar desde el viejo repositorio las funcionalidades que tiene el bot de forma estructurada, prolija y segura. Muy pronto traeremos bardearmarto, tranquilos.

Mientras seguimos la migración todos son libres de colaborar con pull requests.

Para probar el bot en acción en Telegram es necesario crear un archivo `tokenz.py` que asigne a la variable `token` el token del bot con el que se desea hacer las pruebas.

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
