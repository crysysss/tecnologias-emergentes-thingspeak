# plan.md

## Objetivo actual

Mantener una version publicable y autoejecutable de la practica, con backend y
frontend funcionales sobre el canal ThingSpeak de pruebas `3353980`.

## Tareas pendientes

- [x] Extraer requisitos del `docx` grupal y del `pdf` tematico.
- [x] Identificar canal, autor, acceso y credenciales de trabajo.
- [x] Personalizar `AGENTS.md`, `soul.md`, `memory.md` y `ops-rules.md`.
- [x] Crear cambio OpenSpec inicial para el MVP.
- [x] Crear contratos RUNE para payload y escritura controlada.
- [x] Confirmar en ThingSpeak el nombre y orden real de `field1..field5`.
- [x] Crear backend Python con lectura, preview y escritura real.
- [x] Crear frontend Astro con dashboard y formulario operativo.
- [x] Poblar el canal de pruebas con las 10 muestras del PDF.
- [x] Dejar configuracion versionada lista para ejecutar tras clonar el repo.
- [x] Actualizar toda la documentacion principal del proyecto.
- [ ] Inicializar Git local y vincularlo a un repositorio publico.
- [ ] Preparar el ZIP final de entrega o material visual de demostracion si lo quereis.

## Siguiente paso ejecutable

1. inicializar Git en esta carpeta,
2. crear el repo publico en GitHub,
3. hacer `push` del proyecto completo,
4. comprobar desde otra carpeta o equipo que se clona y se ejecuta tal cual.

## Historial de sesiones

### Sesion 2026-04-21
- Que se hizo: se consolidaron requisitos, dataset, backend FastAPI, frontend Astro y modo seguro inicial.
- Que quedo pendiente: habilitar un flujo de escritura controlada sin tocar el canal grupal.

### Sesion 2026-04-22
- Que se hizo: se refactorizo la configuracion a `config/`, se separaron estados reales de lectura, se comento ampliamente el codigo, se poblo el canal `3353980` con las 10 muestras del PDF y se dejo el proyecto listo para publicarse con claves de prueba versionadas.
- Que quedo pendiente: subirlo a GitHub y verificar el clon en limpio.
