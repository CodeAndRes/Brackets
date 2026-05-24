# Backlog Unificado Brackets

Fecha de consolidacion: 2026-05-24

Este backlog centraliza funcionalidades de producto detectadas en:
- SharedContext/MENU_AUDIT_REPORT.md
- brackets/docs/PROPOSITO_ESTRUCTURA_MENU.md
- brackets/docs/pomodoro_spec_v1.md
- brackets/docs/pomodoro_implementation_report.md
- MyJobNotes/[📋PROJECTS][🗃️BRACKETS][📋PLANIFICACION]✅BackLog.md
- MyJobNotes/[📋PROJECTS][🗃️BRACKETS][📋PLANIFICACION]Roadmap.md
- MyJobNotes/[📋PROJECTS][🗃️BRACKETS][📋PLANIFICACION]Main.md
- SharedContext/WORKSTYLE_SYSTEM_SUGGESTIONS.md
- brackets/HANDOFF_PROMPT_CONTEXT_2026-02-22.md

## Paquete de continuidad para nuevo agente

- docs/HANDOFF_AGENTE_SIGUIENTE.md
- docs/PLAN_YAML_RELACIONAL.md

## Kanban continuo (activo desde 2026-05-24)

Modelo operativo:
- Fuente unica: este backlog.
- Estados: `Ideas` -> `Priorizado` -> `En ejecucion` -> `Verificado`.
- Limite WIP: 1 bloque principal simultaneo.
- Checkpoint: revisar y reordenar cada 3-4 movimientos de estado.

Bloque activo (WIP principal):
- [Verificado] Fallback automatico a flujo manual cuando no existen bitacoras previas.

Cola inmediata priorizada:
- [Verificado] Restringir visibilidad de vaults: desde `run_brackets.py` local mostrar solo el vault local; el root mantiene vista global.
- [Verificado] Definir y aplicar una politica unica de versionado (README/setup/modulos internos).

## Implementado

- [x] Desacoplamiento de menu principal y submenus a configuracion YAML.
- [x] Motor de menu reutilizable con `context_tag`, quick-keys y validacion de conflictos de teclas.
- [x] Navegacion de menu sin Enter para seleccion por quick-key.
- [x] Navegacion por flechas (arriba/abajo) + Enter en menus YAML.
- [x] Script de arranque rapido en `C:/Projects/brackets_quickstart.ps1` que activa venv y lo desactiva al finalizar.
- [x] Integracion de Pomodoro v1 en modo standalone y desde el menu/CLI (`--timer`).
- [x] Reporte de implementacion Pomodoro con trazabilidad a spec y criterios de aceptacion PASS.
- [x] VaultManager con selector de vaults, creacion de vault y flujo de entrada interactivo.
- [x] Configuracion viva de patron laboral, festivos y vacaciones en menu de configuracion.
- [x] Separacion fisica core/vault (repo `brackets` desacoplado de vaults).

## Alta prioridad

- [x] Corregir traspaso de tareas entre semanas para no migrar tareas tachadas `[x]` y respetar jerarquias (incluye no migrar subtareas de padre completado).
- [x] Si no hay bitacoras previas, que la opcion "Crear bitacora semanal" redirija automaticamente al flujo manual.
- [ ] Corregir formato del titulo de `MonthTopics` (ejemplo esperado: `# July Topics ☀️`).
- [x] Definir y aplicar una politica unica de versionado (README/setup/modulos internos).
- [x] Restringir visibilidad de vaults: desde `run_brackets.py` local mostrar solo el vault local; el root mantiene vista global.

## Prioridad media

- [ ] Menu por tipo de vault (work/personal) con reglas de visibilidad mas finas (actualmente parcial por `context_tag`).
- [ ] Inyeccion de contexto vivo en dashboard principal (semana actual, estado de bitacora, estado Pomodoro, tareas pendientes).
- [x] Limpieza de pausas no esenciales en la navegacion de menus (quick-keys + flechas + Enter).
- [ ] Añadir smoke test unico para validar vault nuevo en un comando.
- [ ] Crear `MULTIROOT_WORKFLOW.md`.
- [x] Corregir rutas desactualizadas en README de `test-vault` (obsoleto: el repo `test-vault` ya no esta presente en el workspace actual).
- [ ] Modularizar aun mas `main.py` por responsabilidades.
- [ ] Modernizar empaquetado a `pyproject.toml`.

## Configuracion por vault y bitacoras

- [ ] Hacer configurable por vault el bloque de preguntas iniciales semanales (incluyendo peso/salud).
- [ ] Hacer configurable por vault la pregunta de ubicacion (casa/oficina/remoto).
- [ ] Hacer configurable por vault la duracion de semana (5 dias trabajo, 7 dias personal).
- [ ] Definir modo opcional sin dimension temporal (solo notas/proyectos, sin bitacoras semanales).
- [ ] Crear opcion de ejecucion diaria para traspaso de tareas entre dias.
- [ ] Opcion interactiva para anadir tareas del dia en curso.
- [ ] Crear y usar archivo de tareas recurrentes (semanal/mensual/cuatrimestral).

## Modulos funcionales futuros

- [ ] Sistema de tipos de entrada por documento (Topic, Note, Task, Def) con orden configurable.
- [ ] Asistente "siempre escuchando" para crear entradas en dia correcto y en cualquier vault.
- [ ] Crear categoria de tareas programadas y lista de tareas recurrentes autoinsertadas cada semana.
- [ ] Posibilidad de cuentas atras para eventos al inicio de semana.
- [ ] Consulta de prevision meteorologica semanal.
- [ ] Plantilla editable de bitacora semanal con secciones predefinidas.
- [ ] Crear apartado mensual de resumen del mes anterior por semanas.
- [ ] Potenciar sistema de links cruzados entre documentos para navegacion de agentes.

## Nuevas ideas agrupadas por tema (verificadas)

### CLI y punto de entrada

- [x] Brackets estilo CLI (ya existe CLI con `argparse` y entrypoint por `brackets.main`).
- [x] Poner un ejecutable en `C:/Projects/` (existente: `C:/Projects/brackets_quickstart.ps1`).
- [ ] Pensar opciones generales para directorio `Projects` (config global, defaults y comandos de entorno).

### Servicio residente y ejecucion continua

- [ ] Pasarlo a un servicio que arranque solo siempre (Windows Service / Task Scheduler).
- [ ] Que siempre este escuchando (modo daemon/watcher con canal de comandos).

### Tiempo, tareas y bitacora automatica

- [ ] Medicion del tiempo con asignacion de tarea (PARCIAL: hay timer, falta asignacion formal a task-id).
- [ ] Edicion automatica de Bitacora basada en eventos de trabajo.
- [ ] Gestion de tareas por codigo (task-id unico, estado, prioridad y relaciones).

### Motor de documentos y render

- [ ] Modulo de renderizado de `.md` para aplicar cambios estructurados en archivos (ej: backlog).
- [ ] Que `.md` sea solo render de un estado interno (modelo de datos como fuente de verdad).

### IA y resumenes

- [ ] Usar modulo de IA para crear resumenes.
- [ ] Gestion de API Key (segura) para integracion IA.

## Vision de mediano/largo plazo (Roadmap)

- [ ] Fase 4: Modulo de proyectos (estructura, hitos, reporteria, integracion con bitacoras).
- [ ] Fase 5: Modulo de aprendizaje (notas estructuradas, busqueda, resumenes).
- [ ] Fase 6: Automatizacion avanzada (predicciones de tareas, analisis de productividad).
- [ ] Fase 7: Mejoras de interfaz (dashboard enriquecido y posibles exportaciones).
- [ ] Fase 8: YAML-first como persistencia estructurada con modelos y generacion YAML -> Markdown.

## Notas de estado

- La parte de menu quedo funcionalmente adelantada respecto a los checkboxes antiguos de auditoria.
- Se recomienda usar este archivo como unica fuente de backlog funcional y mantener los demas docs como historico/contexto.

## Auditoria tecnica de pendientes

Ultima auditoria: 2026-05-24

- ✅ Traspaso de tareas entre semanas: resuelto y validado en parser/tests (no migra `[x]` ni subtareas de padre completado).
- ✅ Fallback automatico a flujo manual sin bitacoras previas: resuelto en `WeeklyGenerator.create_next_or_manual_weekly_bitacora` + `BitacoraManager.handle_weekly_creation`, validado con `brackets/tests/test_generators_weekly.py`.
- ⏳ Titulo `MonthTopics`: sigue pendiente (actualmente `# {emoji} Topics - Mes {MM}` en `ContentGenerator.create_monthly_topics`).
- ✅ Politica unica de versionado: resuelto con fuente unica en `brackets/version.py`, integrada en `setup.py`, `brackets.__version__` y `config.VERSION`; validado con `brackets/tests/test_version_policy.py`.
- ✅ Visibilidad de vault local vs root: resuelto en `resolve_workspace_context` y flujo de `main`, con tests en `brackets/tests/test_cli_vault_scope.py`.

Regla para marcar una tarea como resuelta:

- Debe existir evidencia en codigo (archivo/metodo) y una verificacion ejecutable (test o comando reproducible).
