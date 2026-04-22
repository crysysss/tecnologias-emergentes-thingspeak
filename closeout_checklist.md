# closeout_checklist.md — Protocolo de Cierre de Sesión

## Disparador

Cuando el usuario dice: "cerramos", "fin de sesión", "hasta luego", "cierre" o equivalente.

## Checklist obligatorio

- [ ] **1. Actualizar plan.md** — Registrar estado actual, próximos pasos y decisiones pendientes
- [ ] **2. Actualizar memory.md** — Añadir decisiones tomadas, hallazgos técnicos y riesgos detectados
- [ ] **3. Revisar soul.md** — ¿Hay que corregir o añadir principios tras lo aprendido?
- [ ] **4. Revisar ops-rules.md** — ¿Nuevas excepciones o restricciones descubiertas?
- [ ] **5. Confirmar archivos modificados** — Listar archivos creados/editados/borrados en esta sesión
- [ ] **6. Verificar estado limpio** — No dejar código a medias sin documentar el estado
- [ ] **7. Resumen al usuario** — Breve resumen de lo conseguido y lo pendiente

## Criterios de calidad

- Ningún archivo modificado sin registrar
- plan.md refleja exactamente el estado real del proyecto
- memory.md contiene todas las decisiones relevantes de la sesión
- El siguiente agente (o sesión) puede retomar el trabajo sin contexto adicional

## Restricciones de entorno (producción)

- **NO** matar procesos que no hayamos lanzado nosotros
- **NO** ejecutar tests que consuman recursos excesivos
- **NO** modificar configuración del sistema
- **NO** dejar servidores de desarrollo corriendo
