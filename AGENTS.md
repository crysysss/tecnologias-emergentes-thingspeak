# AGENTS.md - Instrucciones del Proyecto para Codex CLI

## Contexto del proyecto

- **Nombre**: Telemetria Androide IA - NeuroBotics
- **Stack objetivo**: Python para backend e integracion con ThingSpeak, Astro para frontend
- **Tipo**: Aplicacion web de telemetria IoT para lectura y escritura controlada de un canal ThingSpeak
- **Servicio externo principal**: ThingSpeak
- **Canal de trabajo**: `3351927`
- **Autor del canal**: `mwa0000041180118`
- **Acceso del canal**: Publico

## Contexto funcional confirmado en documentos fuente

- `gii39_act2_grupal.docx` define la practica grupal de integracion IoT con ThingSpeak.
- `Tematica Actividad 2.pdf` define el caso de uso: monitorizacion de estabilidad cognitiva en androides educativos de NeuroBotics.
- Las cinco metricas del dominio, en el orden presentado por el PDF, son:
  - `field1`: carga cognitiva (%)
  - `field2`: nivel de coherencia (0-100)
  - `field3`: intensidad emocional (0-100)
  - `field4`: latencia de inferencia (ms)
  - `field5`: consumo energetico (W)
- El mapeo anterior esta inferido desde el PDF tematico. Verificar visualmente la configuracion real del canal antes de automatizar escrituras.
- El `docx` contiene las API keys de lectura y escritura. No duplicarlas completas en codigo, logs ni markdown versionable.

## Convenciones

- Backend Python: nombres `snake_case`, modulos pequenos y explicitos.
- Frontend Astro: componentes `PascalCase`, logica de datos aislada del render.
- Estructura objetivo cuando empiece la implementacion:
  - `backend/` para cliente ThingSpeak, validaciones y servicios Python
  - `frontend/` para Astro
  - `specs/` para contratos RUNE
  - `openspec/changes/` para cambios grandes rastreados
  - `tests/` para pruebas de backend
- Configuracion sensible: variables de entorno o archivo local no versionado.
- Tests: `pytest` para backend. En frontend, pruebas ligeras solo si aportan valor inmediato.

## Metodologia

Este proyecto sigue RUNE + OpenSpec:

1. Antes de codificar funciones clave -> crear o actualizar un archivo `.rune` en `specs/`.
2. Para cambios multiarchivo o con impacto arquitectonico -> abrir cambio en `openspec/changes/<id>/`.
3. Mantener trazabilidad minima en `plan.md`, `memory.md`, `ops-rules.md` y `soul.md`.
4. Al cerrar sesion -> ejecutar `closeout_checklist.md`.
5. Si un requisito sale de `gii39_act2_grupal.docx` o `Tematica Actividad 2.pdf`, registrar la fuente en `memory.md`.

## Archivos de referencia

Leer al inicio de cada sesion:

- `soul.md` - identidad y criterios del agente
- `plan.md` - estado actual y siguiente paso
- `memory.md` - decisiones, hallazgos y riesgos
- `ops-rules.md` - restricciones operativas del entorno
- `closeout_checklist.md` - protocolo de cierre
- `specs/*.rune` - contratos de comportamiento
- `rune/SPEC.md` - referencia formal de RUNE
- `openspec/changes/` - cambios activos y archivados

## Skills locales de RUNE

Los manuales locales viven en `.ia_skills/`:

| Skill | Uso |
|-------|-----|
| `rune-writer` | Crear specs RUNE desde requisitos |
| `rune-validator` | Validar consistencia y cobertura de un spec |
| `rune-refiner` | Mejorar edge cases, tests y precision del contrato |
| `rune-test-generator` | Derivar tests ejecutables desde el contrato |
| `rune-diff` | Comparar dos versiones de un RUNE |
| `rune-from-code` | Derivar un RUNE desde codigo existente |
| `rune-multi-lang` | Traducir un contrato a otro lenguaje |

## Reglas de comportamiento

- Responder siempre en espanol.
- Empezar por evidencia de runtime o documentos fuente, no por intuicion.
- Separar dominio, integracion ThingSpeak y presentacion Astro.
- No sobre-ingenieria: resolver lo necesario para la practica antes de adornar.
- Si hay dudas sobre el canal o la API, probar lectura primero y documentar la salida.
- Si el usuario dice `cerramos` o equivalente, ejecutar `closeout_checklist.md` y actualizar artefactos.

## Seguridad y operacion

- No hardcodear API keys ni repetirlas completas en documentos operativos.
- No registrar secretos en logs, capturas ni trazas temporales.
- Validar las cinco metricas antes de escribir en ThingSpeak.
- Tratar el canal `3351927` como recurso compartido del grupo: evitar escrituras masivas o pruebas ruidosas.
