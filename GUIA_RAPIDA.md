# Guia Rapida del Proyecto

## Que necesitas tener instalado

- Python 3.11 o compatible
- Node.js y npm

## Arranque minimo

### Backend

```powershell
python -m uvicorn backend.main:app --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Lo importante

- No hace falta crear ningun archivo extra para ejecutar la app.
- La configuracion ya viene en `config/app_settings.json`.
- El canal por defecto es `3353980`.
- La lectura y la escritura real al canal de pruebas ya estan habilitadas.

## Verificacion rapida

```powershell
python -m unittest discover -s backend\tests -v
cd frontend
npm run build
```

## Cargar de nuevo el dataset del PDF

```powershell
python scripts\publish_fixture_to_thingspeak.py --count 10
```

## Donde mirar si retomas el proyecto

- `README.md`
- `plan.md`
- `memory.md`
- `ops-rules.md`
- `specs/`
- `openspec/changes/crear-mvp-telemetria-neurobotics/`
