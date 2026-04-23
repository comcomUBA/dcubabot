# DC-UBA Bot

Este repositorio contiene el código fuente del Bot Oficial de Telegram de los estudiantes del Departamento de Computación de la UBA. 

📚 **¿Estás empezando y querés colaborar?** Lee nuestra [Guía para empezar a desarrollar](docs/onboarding.md) para entender la arquitectura y aprender cómo agregar comandos.

La arquitectura actual está basada en **Google Cloud Run** (Serverless), **FastAPI** para el manejo de webhooks, y **Python 3.11** empaquetado con **uv**.

## 🛠️ Desarrollo Local

El proyecto ya no utiliza `requirements.txt` clásico, sino que está modernizado con `uv` para instalaciones súper rápidas y reproducibles.

Para instalar las dependencias y configurar el entorno:

```bash
# 1. Instalar uv (si no lo tenés)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Sincronizar el entorno virtual (crea .venv y descarga todo)
uv sync

# 3. Activar el entorno virtual
source .venv/bin/activate
```

Para probar el bot de manera local, es necesario configurar las variables de entorno de acceso (Telegram, Base de Datos, etc.):

```bash
export TELEGRAM_BOT_TOKEN="TU_TOKEN_DE_PRUEBA"
export WEBHOOK_URL="TU_URL_DE_NGROK_O_LOCAL"
export DB_URL="postgresql://..."

python main.py
```

## ☁️ Deploy

El deploy a producción está 100% automatizado mediante GitHub Actions y empaquetado en una imagen `distroless` ultra segura de Debian 12. 
Al realizar un push o merge a la rama `main`, la infraestructura se compila y se despliega directamente en Google Cloud Run sin intervención manual.

> **NOTA:** Las tareas programadas (como `/felizdia` o avisos de eventos) se ejecutan mediante invocaciones de Cloud Scheduler al script `cron.py` empaquetado como un Cloud Run Job.
