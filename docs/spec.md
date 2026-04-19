# Especificaciones y Tareas Pendientes (TODOs)

## Optimizaciones de Infraestructura (Cloud Run)
- [ ] **TODO:** Revisar cuánto está gastando de RAM el bot principal en producción.
  - *Contexto:* Por defecto, Cloud Run asigna 512 MB de RAM a cada contenedor. El bot de Telegram probablemente consuma menos (entre 128 MB y 256 MB). Si se desea optimizar al máximo, se podría reducir la memoria asignada en el archivo de despliegue (`.github/workflows/google-cloudrun-docker.yml`) agregando el flag `--memory=256Mi`.
  - *Nota:* Esto es una micro-optimización ya que Cloud Run tiene una capa gratuita generosa y escala a cero, por lo que no genera costos adicionales si no se sobrepasan los límites mensuales.
