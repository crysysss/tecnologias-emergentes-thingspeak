# Telemetria Androide IA - NeuroBotics

Aplicacion de practica para integrar ThingSpeak con una interfaz de monitorizacion
de estabilidad cognitiva en androides educativos. El proyecto esta preparado
para subirse a un repositorio publico y ejecutarse tal cual tras clonarlo.

## Estado actual

- Backend en `backend/` con FastAPI.
- Frontend en `frontend/` con Astro.
- Canal por defecto del proyecto: `3353980`.
- Credenciales de prueba ya incluidas en `config/app_settings.json`.
- Lectura 100% online con distincion entre:
  - `live_data`
  - `live_empty`
- Preview local del payload y escritura real disponible por defecto sobre el canal
  de pruebas.
- El dataset de la practica vive en `backend/data/neurobotics_fixture.json` y se
  usa solo como semilla para poblar ThingSpeak, no como fallback de lectura.
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

### 0. Preparar el entorno

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd frontend
npm install
cd ..
```

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

### Script de arranque rapido

Si prefieres abrir backend y frontend con un solo comando:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1
```

Modo simulacion sin lanzar ventanas:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1 -DryRun
```

## Como probarlo por ti misma

### 1. Arrancar backend y frontend

Abre dos terminales:

- Terminal 1:

```powershell
python -m uvicorn backend.main:app --reload
```

- Terminal 2:

```powershell
cd frontend
npm run dev
```

### 2. Comprobar el backend

Abre la documentacion interactiva:

```text
http://127.0.0.1:8000/docs
```

Prueba estos endpoints:

- `GET /api/health`
  - debe devolver backend operativo y modo de lectura online
- `GET /api/channel`
  - debe devolver el canal configurado y las etiquetas reales de ThingSpeak
- `GET /api/telemetry/history`
  - si el canal tiene datos, devuelve mediciones reales
  - si el canal esta vacio, devuelve `channel_state=live_empty`
  - si ThingSpeak no responde, devuelve `HTTP 503`
- `GET /api/telemetry/latest`
  - debe devolver la ultima medicion real o `live_empty` si no hay datos

### 3. Comprobar el dashboard

Abre:

```text
http://127.0.0.1:4321
```

Verifica:

- si el canal tiene datos, el dashboard muestra solo datos online reales
- si el canal esta vacio, el dashboard indica que el canal esta vacio
- si ThingSpeak falla, el dashboard muestra error de lectura y no rellena con el PDF

### 4. Probar preview y escritura

- pulsa `Previsualizar payload` para validar una muestra sin escribir
- pulsa `Escribir en canal` para enviar una muestra real al canal configurado
- pulsa `Actualizar` para comprobar si aparece la nueva fila en el historico

### 5. Cambiar al canal oficial del grupo

Si quieres probar el repo contra otro canal sin tocar la configuracion versionada,
crea este archivo local:

```text
config/app_settings.local.json
```

Ejemplo:

```json
{
  "thingspeak_channel_id": 1234567,
  "thingspeak_read_api_key": "TU_READ_KEY",
  "thingspeak_write_api_key": "TU_WRITE_KEY",
  "thingspeak_allow_live_reads": true,
  "thingspeak_allow_write": true
}
```

Ese archivo pisa la configuracion base solo en tu maquina y no se sube al repo.

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

Si ThingSpeak no responde o la lectura en vivo esta deshabilitada, los endpoints
de lectura devuelven `HTTP 503` y la interfaz no sustituye esos datos por el
dataset local.

## Escritura real

La escritura real ya viene habilitada por defecto porque este repositorio apunta
al canal de pruebas del proyecto.

## Dataset semilla

El proyecto conserva el dataset original de la practica en:

```text
backend/data/neurobotics_fixture.json
```

Ese archivo no se consulta para pintar el dashboard. Su funcion es servir como
dataset semilla reproducible para cargar muestras en ThingSpeak con el script del
proyecto.

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
