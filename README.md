# Telemetria Androide IA - NeuroBotics

Aplicacion de practica para integrar ThingSpeak con una interfaz de monitorizacion
de estabilidad cognitiva en androides educativos. El proyecto esta preparado
para subirse a un repositorio publico y ejecutarse tal cual tras clonarlo.

## Estado actual

- Backend en `backend/` con FastAPI.
- Frontend en `frontend/` con Astro.
- Canal por defecto del proyecto: `3353980`.
- Credenciales de prueba ya incluidas en `config/app_settings.json`.
- Lectura en vivo con distincion entre:
  - `live_data`,
  - `live_empty`,
  - `fixture_fallback`,
  - `fixture_only`.
- Preview local del payload y escritura real disponible por defecto sobre el canal
  de pruebas.
- El canal de pruebas ya contiene las 10 muestras del PDF de la practica.

## Metricas del dominio

- `field1`: carga cognitiva (%)
- `field2`: nivel de coherencia (0-100)
- `field3`: intensidad emocional (0-100)
- `field4`: latencia de inferencia (ms)
- `field5`: consumo energetico (W)

## Configuracion

### Configuracion versionada lista para usar

El proyecto toma por defecto `config/app_settings.json`. Ese archivo ya contiene
la configuracion completa necesaria para ejecutar la app tras clonar el repo.

Archivo relevante:

```text
config/app_settings.json
```

Incluye:

- `thingspeak_channel_id=3353980`
- `thingspeak_read_api_key`
- `thingspeak_write_api_key`
- `thingspeak_allow_live_reads=true`
- `thingspeak_allow_write=true`

### Override local opcional

Si en el futuro quieres cambiar de canal o de claves sin tocar la configuracion
versionada, puedes crear:

```text
config/app_settings.local.json
```

El proyecto tambien mantiene compatibilidad con `.env` y `.env.local`, pero el
camino principal de configuracion es `config/`.

## Arranque rapido

### 1. Backend

```powershell
python -m uvicorn backend.main:app --reload
```

Backend disponible por defecto en `http://127.0.0.1:8000`.

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend disponible por defecto en `http://127.0.0.1:4321`.

## Endpoints del backend

- `GET /api/health`
- `GET /api/channel`
- `GET /api/telemetry/history?limit=10`
- `GET /api/telemetry/latest`
- `POST /api/telemetry/preview`
- `POST /api/telemetry/write`

## Estados que devuelve la API

- `channel_state=live_data`: ThingSpeak devuelve mediciones completas.
- `channel_state=live_empty`: el canal responde pero aun no tiene muestras utiles.
- `channel_state=fixture_fallback`: la red falla y se usa el dataset del PDF.
- `channel_state=fixture_only`: la lectura en vivo esta deshabilitada por config.

## Escritura real

La escritura real ya viene habilitada por defecto porque este repositorio apunta
al canal de pruebas del proyecto.

### Escribir una sola medicion por API

```json
POST /api/telemetry/write
{
  "cognitive_load_pct": 52.4,
  "coherence_level_pct": 96.8,
  "emotional_intensity_pct": 35.2,
  "inference_latency_ms": 118.6,
  "power_consumption_w": 42.3
}
```

### Publicar el dataset completo del PDF

```powershell
python scripts\publish_fixture_to_thingspeak.py --count 10
```

## Verificacion

- Tests backend:

```powershell
python -m unittest discover -s backend\tests -v
```

- Build frontend:

```powershell
cd frontend
npm run build
```

Resultado verificado en esta sesion:

- tests backend -> OK
- build frontend -> OK
- escritura de 10 muestras en ThingSpeak -> OK
- lectura posterior en vivo -> OK

## Estructura

```text
backend/   API FastAPI, validacion, lectura, escritura y normalizacion ThingSpeak
config/    Configuracion principal lista para ejecutar y overrides opcionales
frontend/  Dashboard Astro
scripts/   Automatizaciones reproducibles, incluida la carga del dataset del PDF
specs/     Contratos RUNE
```

## Documentos de referencia

- `gii39_act2_grupal.docx`
- `Tematica Actividad 2.pdf`
- `specs/construir_payload_thingspeak_estabilidad.rune`
- `specs/preparar_escritura_controlada_thingspeak.rune`
