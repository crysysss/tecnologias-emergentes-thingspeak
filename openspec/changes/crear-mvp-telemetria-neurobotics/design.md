# Diseno: MVP de telemetria NeuroBotics

## Arquitectura propuesta

### Backend Python

- `config.py`
  - fusiona configuracion versionada, override local y entorno
- `thingspeak_client.py`
  - encapsula lectura y escritura HTTP hacia ThingSpeak
- `service.py`
  - valida datos, mapea campos, clasifica estados y expone operaciones de aplicacion
- `tests/test_api.py`
  - cubre fixture local, canal vacio, escritura bloqueada y escritura aceptada

### Frontend Astro

- pagina de dashboard con:
  - metadata del canal configurado,
  - ultima medicion,
  - tabla de historico reciente,
  - preview local,
  - boton de escritura real cuando el backend la habilita.

### Scripts

- `scripts/publish_fixture_to_thingspeak.py`
  - publica las 10 muestras del PDF respetando el retardo configurado entre escrituras.

## Decisiones tecnicas

1. El proyecto distribuido apunta por defecto al canal publico de pruebas `3353980`.
2. Las claves sensibles no viven en archivos versionados: solo en `config/app_settings.local.json`.
3. La escritura real ya no depende de una confirmacion en el payload HTTP; la barrera operativa se mueve a la configuracion local.
4. El backend clasifica la lectura en cuatro estados para que la UI no mezcle canal vacio con fallback de red.
5. Preview y escritura real reutilizan el mismo bloque de validacion para no divergirse.

## Flujo de alto nivel

1. El frontend solicita `/api/channel`, `/api/telemetry/history` y `/api/telemetry/latest`.
2. El backend intenta leer ThingSpeak.
3. Si hay datos validos, responde `live_data`.
4. Si el canal responde pero no tiene muestras completas, responde `live_empty`.
5. Si la red falla, responde `fixture_fallback` con el dataset del PDF.
6. Cuando la configuracion local habilita escritura, el frontend puede llamar a `/api/telemetry/write`.
7. Para poblar el canal de pruebas con el dataset completo, se usa el script CLI.
