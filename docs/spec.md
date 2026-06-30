# Especificaciones y Tareas Pendientes (TODOs)

## Optimizaciones de Infraestructura (Cloud Run)
- [x] **Optimización de RAM en producción:**
  - *Contexto:* Se midió el uso de RAM del Cron Job y rondaba los 92 MB. Se optimizó su configuración a **128Mi** de RAM en los archivos de despliegue.
  - *Bot Principal:* Está configurado con un límite de **256Mi** en los archivos de despliegue (`.github/workflows/google-cloudrun-docker.yml` y `cloudbuild.yaml`).
  - *Diagnóstico:* Se eliminó la medición y reporte automático de RAM en `cron.py` para evitar spam de diagnóstico innecesario.
