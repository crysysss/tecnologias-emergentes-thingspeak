# Diseno: MVP de telemetria NeuroBotics

## Rol de este documento

Este `design.md` no duplica el detalle de comportamiento. Su funcion es actuar
como mapa de arquitectura y apuntar a los contratos RUNE que definen la logica
estable del proyecto.

## Contratos fuente de verdad

- `specs/construir_payload_thingspeak_estabilidad.rune`
  - contrato de validacion, normalizacion y mapeo de las cinco metricas hacia
    `field1..field5`
- `specs/preparar_escritura_controlada_thingspeak.rune`
  - contrato del flujo de preview, escritura real y semantica operativa del
    canal ThingSpeak configurado

## Arquitectura aplicada

### Backend Python

- `backend/config.py`
  - carga la configuracion versionada desde `config/app_settings.json`
  - acepta override local opcional sin romper la ejecucion distribuible
- `backend/thingspeak_client.py`
  - encapsula lectura y escritura HTTP contra ThingSpeak
- `backend/service.py`
  - aplica las reglas del dominio y transforma la respuesta de ThingSpeak al
    modelo comun de la app
  - mantiene lectura online estricta: solo `live_data` o `live_empty`
- `backend/main.py`
  - expone la API FastAPI y convierte fallos de lectura remota en `HTTP 503`
- `backend/tests/test_api.py`
  - valida canal vacio, lectura no disponible, preview y escritura aceptada

### Frontend Astro

- `frontend/src/pages/index.astro`
  - consume la API del backend
  - muestra solo datos online reales, o bien el estado de canal vacio / lectura
    no disponible
  - no usa el dataset semilla para rellenar la interfaz

### Dataset y scripts

- `backend/data/neurobotics_fixture.json`
  - dataset semilla derivado de la practica
  - se conserva para poblar canales ThingSpeak, no como fallback visual
- `scripts/publish_fixture_to_thingspeak.py`
  - publica el dataset semilla en el canal configurado respetando el retardo
    minimo entre escrituras

## Decisiones tecnicas vigentes

1. El proyecto distribuido apunta por defecto al canal publico de pruebas `3353980`.
2. El repositorio queda ejecutable tras clonarlo porque `config/app_settings.json`
   incluye la configuracion necesaria del canal de pruebas.
3. Preview y escritura real comparten la misma validacion para no divergir.
4. La lectura del dashboard es 100% online: si ThingSpeak falla, la API informa
   del error y no sustituye datos por el dataset local.
5. El dataset original de la practica se mantiene solo como semilla reproducible
   para cargar canales y para trazabilidad academica.

## Flujo de alto nivel

1. El frontend solicita `/api/channel`, `/api/telemetry/history` y `/api/telemetry/latest`.
2. El backend consulta ThingSpeak usando el cliente HTTP dedicado.
3. Si existen mediciones completas, responde `live_data`.
4. Si el canal existe pero no tiene filas completas, responde `live_empty`.
5. Si ThingSpeak no responde o la lectura esta deshabilitada, el backend devuelve `HTTP 503`.
6. El usuario puede validar un payload con `/api/telemetry/preview`.
7. Si la escritura esta habilitada, `/api/telemetry/write` envia la muestra al canal.
8. Para sembrar el canal con el dataset de referencia, se usa el script CLI.
