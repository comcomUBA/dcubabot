# 🤖 dcubabot

[![Build Status](https://github.com/cavazquez/dcubabot/actions/workflows/check.yml/badge.svg)](https://github.com/cavazquez/dcubabot/actions)
[![Repo Size](https://img.shields.io/github/repo-size/cavazquez/dcubabot)](https://github.com/cavazquez/dcubabot)
[![Code Size](https://img.shields.io/github/languages/code-size/cavazquez/dcubabot)](https://github.com/cavazquez/dcubabot)
[![Issues](https://img.shields.io/github/issues/cavazquez/dcubabot)](https://github.com/cavazquez/dcubabot/issues)
[![Last Commit](https://img.shields.io/github/last-commit/cavazquez/dcubabot)](https://github.com/cavazquez/dcubabot)
[![License](https://img.shields.io/github/license/cavazquez/dcubabot)](https://github.com/cavazquez/dcubabot/blob/master/LICENSE)

Bot de Telegram para la comunidad del Departamento de Computación de la Facultad de Ciencias Exactas y Naturales (UBA).

La idea de este repositorio es migrar las funcionalidades del bot original de forma estructurada, prolija y segura.

---

## ✨ Funcionalidades

El bot ofrece una variedad de herramientas útiles para los estudiantes:

- 🏫 **Campus Vivo:** Chequeo en tiempo real del estado del campus virtual.
- 📅 **Finales:** Cálculo de fechas de vencimiento de finales aprobados.
- 🏟️ **River Plate:** Avisos de cuando juega River de local o hay conciertos (para evitar el caos de las aulas de Ciudad Universitaria).
- 🧪 **Laboratorios:** Consulta de disponibilidad y eventos en los laboratorios de computación.
- 📁 **Repositorio de Material:** Acceso rápido a apuntes, planos de estudios y archivos útiles.
- 📢 **Noticias y Sugerencias:** Sistema para proponer noticias y mejoras al bot.
- 💬 **Grupos:** Listado dinámico de grupos de materias (obligatorias, optativas, ECI).

---

## 🛠️ Stack Tecnológico

### Ecosistema de Desarrollo
- **Python 3.13**: Lenguaje principal.
- **[uv](https://docs.astral.sh/uv/)**: Gestión ultrarrápida de paquetes y entornos virtuales.
- **[ruff](https://docs.astral.sh/ruff/)**: Linter y formatter de alto rendimiento.
- **[mypy](https://mypy.readthedocs.io/)**: Verificación estática de tipos.

### Dependencias Principales
- **[python-telegram-bot](https://python-telegram-bot.org/)**: Interfaz con la API de Telegram.
- **[Pony ORM](https://ponyorm.org/)**: Mapeo objeto-relacional simple y potente.
- **[icalevents](https://github.com/irgangla/icalevents)**: Manejo de calendarios iCal.
- **[requests](https://requests.readthedocs.io/)**: Peticiones HTTP.

---

## 🚀 Instalación y Uso

### 1. Clonar y configurar
Asegurate de tener `uv` instalado. Si no lo tenés:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Configurar Token
Creá un archivo `tokenz.py` en la raíz del proyecto:
```python
token = "TU_TOKEN_DE_TELEGRAM_AQUI"
```

### 3. Ejecutar
```bash
# Sincronizar dependencias e instalar entorno
uv sync

# Inicializar base de datos (solo la primera vez)
uv run python install.py

# Iniciar el bot
uv run python dcubabot.py
```

### 4. Mantener la calidad del código
Para correr el linter, formatter y chequeo de tipos:
```bash
./check.sh
```

---

## 🤝 Contribuciones

¡Todas las contribuciones son bienvenidas! Podés ayudar reportando bugs, sugiriendo nuevas funcionalidades o enviando un Pull Request.

- **Issues:** [Reportar un problema](https://github.com/comcomUBA/dcubabot/issues)
- **PRs:** Asegurate de correr `./check.sh` antes de subir tus cambios.

---

Desarrollado con ❤️ para la comunidad del DC.
