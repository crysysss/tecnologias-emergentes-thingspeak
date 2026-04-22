# Tareas: MVP de telemetria NeuroBotics

## Estado: IMPLEMENTADO Y REFACORIZADO PARA CANAL DE PRUEBAS

### Tarea 1: Formalizar el dominio y el alcance
- [x] Extraer requisitos desde `gii39_act2_grupal.docx`
- [x] Extraer tematica y dataset desde `Tematica Actividad 2.pdf`
- [x] Registrar restricciones y riesgos en `memory.md` y `ops-rules.md`
- [x] Crear contratos RUNE para payload y escritura controlada
- [x] Confirmar en ThingSpeak el orden real de `field1..field5`

### Tarea 2: Preparar backend Python
- [x] Crear estructura `backend/`
- [x] Crear modulo de configuracion con `config/app_settings.json`
- [x] Crear modelo de medicion del dominio
- [x] Crear cliente ThingSpeak de lectura y escritura
- [x] Crear validaciones de rangos y tipos
- [x] Diferenciar `live_data`, `live_empty`, `fixture_fallback` y `fixture_only`

### Tarea 3: Habilitar escritura controlada
- [x] Implementar mapeo de metricas a `field1..field5`
- [x] Implementar operacion de escritura con control de errores
- [x] Mantener la habilitacion de escritura en config local, no en archivos versionados
- [x] Crear script para publicar el dataset del PDF

### Tarea 4: Crear frontend Astro
- [x] Crear estructura `frontend/`
- [x] Mostrar ultima medicion y tabla de historico reciente
- [x] Mostrar estado real del canal vacio frente a fallback local
- [x] Crear formulario para preview y escritura real cuando el backend la habilita

### Tarea 5: Verificacion y entrega
- [x] Probar backend
- [x] Compilar frontend
- [x] Documentar instalacion, configuracion y operaciones soportadas
- [x] Revisar que no haya secretos en codigo ni en markdown versionado
- [ ] Poblar el canal de pruebas con las 10 muestras del PDF y verificar lectura en vivo
- [ ] Preparar material final para la entrega ZIP
