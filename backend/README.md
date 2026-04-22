# Backend NeuroBotics

API FastAPI para lectura, normalizacion y escritura controlada sobre ThingSpeak.

## Que hace el backend

- Lee el canal ThingSpeak configurado en `config/app_settings.json`.
- Si ThingSpeak responde pero el canal esta vacio, devuelve `channel_state=live_empty`.
- Si ThingSpeak no responde o la lectura online esta deshabilitada, devuelve `HTTP 503`.
- Permite preview local del payload sin tocar la red.
- Permite escritura real por defecto porque el proyecto versionado ya incluye las
  claves de prueba del canal `3353980`.

## Arranque

```powershell
python -m uvicorn backend.main:app --reload
```

## Endpoints

- `GET /api/health`
- `GET /api/channel`
- `GET /api/telemetry/history?limit=10`
- `GET /api/telemetry/latest`
- `POST /api/telemetry/preview`
- `POST /api/telemetry/write`

## Configuracion

### Base versionada

```text
config/app_settings.json
```

Ese archivo ya deja el backend listo para funcionar tras clonar el repositorio.

### Override local opcional

```text
config/app_settings.local.json
```

Solo hace falta si quieres cambiar canal, claves o flags sin editar el archivo
versionado.

## Verificacion recomendada

```powershell
python -m unittest discover -s backend\tests -v
```

## Carga automatizada del dataset de la practica

```powershell
python scripts\publish_fixture_to_thingspeak.py --count 10
```

El script reutiliza la misma validacion que la API y respeta el retardo entre
escrituras definido en configuracion. El dataset JSON se conserva para poblar el
canal de ThingSpeak, no como fallback de lectura del dashboard.
