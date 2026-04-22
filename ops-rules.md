# ops-rules.md - Excepciones y Restricciones de Runtime

## Entorno

- **Tipo:** practica academica con ThingSpeak real
- **Canal operativo por defecto:** `3353980`
- **Canal a proteger:** `3351927`

## Excepciones activas

| ID | Excepcion | Motivo | Fecha inicio | Fecha fin estimada |
|----|-----------|--------|-------------|-------------------|
| 1 | Se permite lectura y escritura real sobre el canal `3353980`. | Es el canal de pruebas oficial del proyecto y sus claves de prueba van versionadas. | 2026-04-22 | Mientras el canal siga siendo de pruebas |
| 2 | Se prohiben escrituras automatizadas sobre el canal grupal `3351927`. | El historico del canal forma parte de la entrega compartida. | 2026-04-21 | Permanente salvo decision explicita del grupo |

## Restricciones temporales

- Si el canal de pruebas cambia de claves, actualizar `config/app_settings.json`.
- Si el proyecto deja de ser publicable con claves expuestas, migrar de nuevo a `config/app_settings.local.json`.

## Hallazgos de runtime

- El directorio actual no estaba versionado con Git al inicio de esta sesion.
- El sandbox no puede alcanzar ThingSpeak; las operaciones reales de lectura y escritura se verificaron fuera del sandbox.
- A fecha `2026-04-22`, el canal `3353980` contiene las 10 muestras del dataset del PDF y la app lee `live_data`.
