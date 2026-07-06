# Especificaciones y Tareas Pendientes (TODOs)

## Optimizaciones de Infraestructura (Cloud Run)
- [x] **Optimización de RAM en producción:**
  - *Contexto:* Se midió el uso de RAM del Cron Job y rondaba los 92 MB. Se configuró su RAM en **512Mi** (el mínimo permitido por Google Cloud Run para Jobs de segunda generación, ya que no admite menos de 512Mi).
  - *Bot Principal:* Está configurado con un límite de **256Mi** en los archivos de despliegue (`.github/workflows/google-cloudrun-docker.yml` y `cloudbuild.yaml`).
  - *Diagnóstico:* Se eliminó la medición y reporte automático de RAM en `cron.py` para evitar spam de diagnóstico innecesario.
