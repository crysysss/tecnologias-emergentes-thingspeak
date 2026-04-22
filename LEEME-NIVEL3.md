# LEEME Nivel 3 del Proyecto

Este repositorio ya esta preparado para publicarse tal cual y ejecutarse tras
clonarlo. El canal de pruebas y sus claves de prueba forman parte del estado
versionado del proyecto.

## Principios practicos

- La configuracion principal vive en `config/app_settings.json`.
- El canal grupal `3351927` no se usa para pruebas automatizadas.
- El canal de pruebas `3353980` es el entorno por defecto del repositorio.
- Backend y frontend estan comentados para que el equipo entienda el flujo.

## Dónde esta la logica importante

- `backend/config.py`: fusion y lectura de configuracion
- `backend/thingspeak_client.py`: acceso HTTP real a ThingSpeak
- `backend/service.py`: validacion, normalizacion y estados de lectura
- `frontend/src/pages/index.astro`: UI y consumo de la API
- `scripts/publish_fixture_to_thingspeak.py`: carga automatica del dataset del PDF

## Dónde esta la trazabilidad

- `plan.md`
- `memory.md`
- `ops-rules.md`
- `specs/`
- `openspec/changes/crear-mvp-telemetria-neurobotics/`

## Que significa que la app funciona

- Compila backend y frontend
- Lee datos reales del canal de pruebas
- Puede escribir una medicion real en el canal de pruebas
- Cualquier persona que clone el repo puede arrancarla sin configuracion extra
