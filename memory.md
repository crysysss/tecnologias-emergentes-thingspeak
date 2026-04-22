# memory.md

## Decisiones tomadas

| Fecha | Decision | Razon |
|-------|----------|-------|
| 2026-04-21 | Tomar `gii39_act2_grupal.docx` y `Tematica Actividad 2.pdf` como fuentes primarias del alcance funcional. | Son los documentos que fijan la practica, el canal y la tematica exacta. |
| 2026-04-21 | Usar Python para backend e integracion con ThingSpeak y Astro para frontend. | Coincide con la preferencia operativa del proyecto y de Cristina. |
| 2026-04-21 | Implementar lectura con fallback al dataset local del PDF. | Permite demostrar la app incluso si falla la red. |
| 2026-04-22 | Usar el canal de pruebas `3353980` como runtime por defecto del proyecto. | Evita contaminar el canal grupal y permite demo real. |
| 2026-04-22 | Versionar en `config/app_settings.json` las claves de prueba del canal. | Cristina quiere que cualquier persona que clone el repo pueda ejecutarlo tal cual sin configuracion extra. |
| 2026-04-22 | Mantener `config/app_settings.local.json` solo como override opcional futuro. | Sigue siendo util si el equipo quiere cambiar de canal o claves sin tocar el archivo versionado. |
| 2026-04-22 | Eliminar la confirmacion manual `confirm_live_write` del payload HTTP. | La autorizacion ya no depende del formulario sino del hecho de que el repo apunta a un canal de pruebas. |
| 2026-04-22 | Comentar el codigo de forma pedagogica en backend, frontend y scripts. | Cristina pidio que todos los companeros y el profesor puedan entender el flujo. |

## Hallazgos tecnicos

### Alcance de la practica

- La practica grupal es de **integracion de sistemas IoT** sobre ThingSpeak.
- La entrega debe incluir:
  - canal creado y funcional,
  - aplicacion que gestione lecturas y escrituras por API,
  - breve documentacion de funcionamiento e instalacion,
  - codigo fuente dentro del ZIP final.

### Datos del canal del grupo

- `Channel ID`: `3351927`
- `Author`: `mwa0000041180118`
- `Access`: `Public`

### Datos del canal de pruebas

- `Channel ID`: `3353980`
- `Name`: `Telemetría Androide IA - NeuroBotics_PRUEBAS`
- `Author`: `mwa0000041180118`
- `Access`: `Public`
- Labels verificados:
  - `field1`: `Carga cognitiva (%)`
  - `field2`: `Nivel de coherencia (0-100)`
  - `field3`: `Intensidad emocional (0-100)`
  - `field4`: `Latencia de inferencia (ms)`
  - `field5`: `Consumo energético (W)`

### Dataset del PDF ya publicado en ThingSpeak

- Se escribieron correctamente las 10 muestras del PDF.
- ThingSpeak devolvio `entry_id` del `1` al `10`.
- La ultima medicion real confirmada es:
  - `entry_id=10`
  - `cognitive_load_pct=95.8`
  - `coherence_level_pct=67.9`

### Implementacion realizada

- Backend FastAPI con:
  - `GET /api/health`
  - `GET /api/channel`
  - `GET /api/telemetry/history`
  - `GET /api/telemetry/latest`
  - `POST /api/telemetry/preview`
  - `POST /api/telemetry/write`
- Configuracion principal en `config/app_settings.json` lista para ejecutar.
- Frontend Astro con lectura, preview y escritura real.
- Script `scripts/publish_fixture_to_thingspeak.py` para recargar el dataset del PDF.
- Comentarios pedagogicos extensos en backend, frontend y script.

### Verificaciones ejecutadas

- `python -m unittest discover -s backend\\tests -v` -> OK
- `npm run build` en `frontend/` -> OK
- `python scripts\\publish_fixture_to_thingspeak.py --count 10` -> OK
- Lectura posterior -> `history.source=live`, `history.channel_state=live_data`, `history.count=10`

## Riesgos detectados

- Al subir el repo como publico, las claves de prueba quedaran expuestas de forma permanente en el historial Git.
- Si en el futuro ese canal deja de ser de prueba o rota claves, habra que actualizar `config/app_settings.json`.
- El canal grupal `3351927` no debe usarse para automatismos de prueba.

## Estado de ultima sesion

- Fecha: 2026-04-22
- Resumen: el proyecto quedo preparado para subirse a un repo publico y ejecutarse tal cual al clonarlo, incluyendo las claves de prueba en la configuracion versionada.
- Siguiente paso: inicializar Git, crear el repo publico y hacer el primer `push`.
