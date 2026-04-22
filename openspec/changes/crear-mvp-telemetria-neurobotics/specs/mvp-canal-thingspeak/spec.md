# Spec: Gestion del canal ThingSpeak para estabilidad cognitiva

## Reglas de negocio

### Lectura del canal

- La aplicacion DEBE recuperar el historico JSON del canal configurado en `config/app_settings.json`.
- La aplicacion DEBE poder recuperar la ultima medicion completa del canal.
- La aplicacion DEBE permitir limitar el numero de resultados leidos para no traer mas historial del necesario.
- La aplicacion DEBE distinguir entre canal con datos reales, canal vacio y fallback local por error de lectura.

### Escritura de mediciones

- La aplicacion DEBE escribir las cinco metricas del dominio en una sola operacion.
- La aplicacion NO DEBE escribir si falta cualquiera de las cinco metricas.
- La aplicacion DEBE validar rangos y tipos antes de llamar a ThingSpeak.
- La aplicacion DEBE permitir preview local sin tocar la red.
- La aplicacion DEBE permitir escritura real solo cuando la configuracion local habilita `WRITE_API_KEY` y `thingspeak_allow_write=true`.

### Mapeo de campos

| Campo | Significado | Unidad | Fuente |
|------|-------------|--------|--------|
| `field1` | carga cognitiva | % | PDF tematico + canal de pruebas verificado |
| `field2` | nivel de coherencia | 0-100 | PDF tematico + canal de pruebas verificado |
| `field3` | intensidad emocional | 0-100 | PDF tematico + canal de pruebas verificado |
| `field4` | latencia de inferencia | ms | PDF tematico + canal de pruebas verificado |
| `field5` | consumo energetico | W | PDF tematico + canal de pruebas verificado |

### Validaciones

- `carga_cognitiva` DEBE estar entre `0` y `100`.
- `nivel_coherencia` DEBE estar entre `0` y `100`.
- `intensidad_emocional` DEBE estar entre `0` y `100`.
- `latencia_inferencia_ms` NO DEBE ser negativa.
- `consumo_energetico_w` NO DEBE ser negativo.

### Interfaz y documentacion

- La interfaz DEBE mostrar con claridad si esta leyendo `live_data`, `live_empty`, `fixture_fallback` o `fixture_only`.
- La instalacion DEBE documentar `config/app_settings.json` y `config/app_settings.local.json`.
- La documentacion DEBE explicar como usar el dataset del PDF para validar y poblar el canal de pruebas.
