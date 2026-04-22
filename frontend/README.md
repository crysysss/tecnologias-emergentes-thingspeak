# Frontend Astro

Frontend del panel de telemetria de NeuroBotics.

## Requisitos

- Node.js 20 o superior
- Backend FastAPI escuchando por defecto en `http://127.0.0.1:8000`

## Variables publicas opcionales

- `PUBLIC_BACKEND_URL`: URL base del backend

## Arranque

```bash
npm install
npm run dev
```

## Contrato esperado del backend

- `GET /api/health`
- `GET /api/channel`
- `GET /api/telemetry/latest`
- `GET /api/telemetry/history?limit=10`
- `POST /api/telemetry/preview`

La UI no escribe en ThingSpeak. Solo pide una previsualizacion del payload al backend.
