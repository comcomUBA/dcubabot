# 🗺️ Roadmap de Mejoras - dcubabot

Este documento detalla las ideas propuestas para mejorar la robustez, mantenibilidad y funcionalidades del bot.

---

## 🏗️ 1. Arquitectura y Mantenibilidad
El bot ha crecido considerablemente y beneficiaría de una estructura más modular.

- [ ] **Modularización de Handlers**: Separar `dcubabot.py` en módulos (ej. `handlers/`, `commands/`, `core/`).
- [ ] **Limpieza de Globales**: Refactorizar el uso de variables globales para usar una estructura de aplicación más limpia.
- [ ] **CONTRIBUTING.md**: Crear una guía clara para que nuevos colaboradores sepan cómo configurar `uv`, `ruff` y `mypy`.

## 🧪 2. Calidad de Código y Testing
Asegurar que las funcionalidades core no se rompan con cambios futuros.

- [ ] **Suite de Tests (Pytest)**: Implementar tests unitarios para:
    - [ ] Lógica de vencimiento de finales (`vencimientoFinales.py`).
    - [ ] Utilidades de calendario (`calendario.py`).
    - [ ] Parseo de fechas y comandos.
- [ ] **CI/CD Mejorado**: Integrar los tests en el workflow de Github Actions.

## 🐳 3. Infraestructura y Despliegue
Facilitar la ejecución del bot en cualquier entorno.

- [ ] **Dockerización**: 
    - [ ] Crear `Dockerfile` optimizado (usando imágenes livianas de Python).
    - [ ] Crear `docker-compose.yml` para levantar el bot y el volumen de la base de datos fácilmente.
- [ ] **Manejo de Secretos**: Migrar `tokenz.py` a variables de entorno o archivos `.env`.

## ✨ 4. Nuevas Funcionalidades
Mejorar la utilidad del bot para los estudiantes.

- [ ] **Comando `/calendario`**: Integrar el calendario académico oficial (inscripciones, feriados, fechas de exámenes).
- [ ] **Sistema de Notificaciones por Materia**: Permitir que los usuarios se suscriban a novedades de materias específicas.
- [ ] **Dashboard de Estadísticas**: Comando `/stats` para administradores (uso de comandos, usuarios únicos, etc.).

---
*Para empezar con cualquiera de estas tareas, simplemente indicalo y lo ponemos en marcha.*
