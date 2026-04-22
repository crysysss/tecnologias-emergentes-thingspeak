# Propuesta: MVP de telemetria NeuroBotics sobre ThingSpeak

## Resumen

Construir y dejar publicable una aplicacion ligera con backend Python y frontend
Astro para leer, visualizar y escribir mediciones de estabilidad cognitiva sobre
ThingSpeak.

## Motivacion

La practica exige una aplicacion capaz de consumir las APIs de ThingSpeak para
leer y escribir datos. Cristina quiere que el repositorio publico sea ejecutable
tal cual por cualquier profesor o companero tras clonarlo.

## Alcance

### Incluido

- Configuracion versionada completa en `config/app_settings.json`
- Lectura y escritura real sobre el canal de pruebas `3353980`
- Distincion explicita entre `live_data`, `live_empty`, `fixture_fallback` y `fixture_only`
- Frontend Astro operativo
- Script para publicar el dataset del PDF
- Documentacion actualizada para repositorio publico autoejecutable

### Excluido

- Uso del canal grupal como entorno de pruebas automatizadas
- Analitica predictiva avanzada
- Persistencia propia fuera de ThingSpeak

## Impacto

- El proyecto puede subirse a GitHub y funcionar sin configuracion manual
- Las claves de prueba pasan a formar parte del estado versionado del proyecto
- La responsabilidad de rotarlas en el futuro queda explicitamente documentada
