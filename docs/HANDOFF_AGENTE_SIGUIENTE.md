# Handoff Maestro para Siguiente Agente

Fecha: 2026-05-24
Objetivo: permitir continuidad total en chat nuevo sin perder contexto tecnico ni prioridades.

## Lectura obligatoria (orden)

1. docs/BACKLOG_UNIFICADO.md
2. docs/PLAN_YAML_RELACIONAL.md
3. docs/PROPOSITO_ESTRUCTURA_MENU.md
4. docs/pomodoro_spec_v1.md
5. docs/pomodoro_implementation_report.md

## Estado actual verificado

- Menus desacoplados a YAML con quick-keys y navegacion por flechas+Enter.
- Script rapido de arranque en C:/Projects/brackets_quickstart.ps1.
- Pomodoro v1 funcional con pausa/resume y resumen de sesiones.
- Traspaso de tareas corregido para no migrar [x] y no migrar subtareas bajo padre completado.
- Fallback automatico semanal: si no hay bitacora previa, redirige a flujo manual.
- Visibilidad de vaults por contexto: local muestra solo su vault; root mantiene selector global.
- Politica de versionado unificada: fuente unica en brackets/version.py para runtime y packaging.
- Formato MonthTopics alineado a objetivo: # {MonthName} Topics {emoji}.

## Pendientes tecnicos criticos (confirmados)

- Modularizar aun mas brackets/main.py por responsabilidades.
- Definir menu por tipo de vault (work/personal) con reglas de visibilidad mas finas.
- Añadir smoke test unico para validar vault nuevo en un comando.
- Modernizar empaquetado a pyproject.toml.

## Registro de avances recientes (bitacora de ejecucion)

Fecha de corte: 2026-05-24

- Bloque resuelto: fallback automatico semanal (auto -> manual sin base previa).
  - Evidencia: brackets/generators/weekly.py, brackets/main.py, brackets/tests/test_generators_weekly.py.
- Bloque resuelto: alcance de vault por contexto de ejecucion (local/root).
  - Evidencia: brackets/main.py (resolve_workspace_context), brackets/tests/test_cli_vault_scope.py.
- Bloque resuelto: versionado unico runtime + setup.
  - Evidencia: brackets/version.py, brackets/config.py, brackets/__init__.py, setup.py, brackets/tests/test_version_policy.py.
- Bloque resuelto: formato de titulo MonthTopics.
  - Evidencia: brackets/utils/content_generator.py, brackets/tests/test_utils_content_generator.py.
- Bloque incremental: modularizacion de main.py iniciada con extraccion de contexto de workspace.
  - Evidencia: brackets/core/workspace_context.py, brackets/main.py, brackets/tests/test_cli_vault_scope.py.
- Bloque incremental: extraccion de dispatcher de flags CLI fuera de main.py.
  - Evidencia: brackets/core/cli_actions.py, brackets/main.py, brackets/tests/test_core_cli_actions.py.
- Bloque incremental: extraccion del flujo de seleccion de vault a orquestador core.
  - Evidencia: brackets/core/vault_selection.py, brackets/main.py, brackets/tests/test_core_vault_selection.py.
- Bloque incremental: extraccion del builder de argparse a modulo core.
  - Evidencia: brackets/core/cli_parser.py, brackets/main.py, brackets/tests/test_core_cli_parser.py.
- Bloque incremental: extraccion de la orquestacion de arranque CLI a modulo core.
  - Evidencia: brackets/core/startup.py, brackets/main.py, brackets/tests/test_core_startup.py.
- Bloque incremental: extraccion del flujo de configuración a controlador dedicado.
  - Evidencia: brackets/core/configuration_controller.py, brackets/main.py, brackets/tests/test_core_configuration_controller.py.
- Bloque incremental: extraccion del flujo de herramientas/debug a controlador dedicado.
  - Evidencia: brackets/core/tools_controller.py, brackets/main.py, brackets/tests/test_core_tools_controller.py.
- Bloque incremental: extraccion del flujo de file-management/list/analyze a controlador dedicado.
  - Evidencia: brackets/core/file_management_controller.py, brackets/main.py, brackets/tests/test_core_file_management_controller.py, brackets/tests/test_suite.py.
- Bloque incremental: extraccion del flujo de category-management a controlador dedicado.
  - Evidencia: brackets/core/category_management_controller.py, brackets/main.py, brackets/tests/test_core_category_management_controller.py, brackets/tests/test_suite.py.
- Bloque incremental: extraccion de la orquestacion de sync-yaml a controlador dedicado.
  - Evidencia: brackets/core/sync_yaml_controller.py, brackets/main.py, brackets/tests/test_core_sync_yaml_controller.py, brackets/tests/test_suite.py.
- Bloque incremental: extraccion del flujo de file-rename/global-replace a controlador dedicado.
  - Evidencia: brackets/core/file_rename_controller.py, brackets/main.py, brackets/tests/test_core_file_rename_controller.py, brackets/tests/test_suite.py.

## Estado exacto para retomar (sin releer todo el repo)

- Rama de trabajo activa esperada: feature/evolution-lead-kanban.
- Backlog canonico: docs/BACKLOG_UNIFICADO.md.
- Principio operativo vigente: WIP=1 bloque funcional por iteracion, commit modular tipo Lego.
- Ultimo objetivo funcional cerrado: normalizacion de titulo MonthTopics.
- Ultimo objetivo tecnico incremental: extraccion de resolve_workspace_context fuera de main.py.
- Ultimo objetivo tecnico incremental: extraccion de dispatcher CLI (has_action_flags/dispatch_cli_action).
- Ultimo objetivo tecnico incremental: extraccion de seleccion de vault (selector global/create/cancel/local).
- Ultimo objetivo tecnico incremental: extraccion de parser CLI (build_cli_parser).
- Ultimo objetivo tecnico incremental: extraccion de startup flow (run_startup_flow).
- Ultimo objetivo tecnico incremental: extraccion de controller de configuración.
- Ultimo objetivo tecnico incremental: extraccion de tools controller.
- Ultimo objetivo tecnico incremental: extraccion de file-management/list/analyze controller.
- Ultimo objetivo tecnico incremental: extraccion de category-management controller.
- Ultimo objetivo tecnico incremental: extraccion de sync-yaml controller.
- Ultimo objetivo tecnico incremental: extraccion de file-rename/global-replace controller.
- Siguiente bloque recomendado: extraer debug-tools legacy flow a controlador dedicado para seguir adelgazando BitacoraManager.

## Vision objetivo del usuario

Construir un sistema de gestion de trabajo (notas y tareas) con modelo relacional, pero persistido en YAML.
Markdown debe ser una vista/render de lo que pasa en el motor interno.

## Alcance inmediato recomendado (MVP de base de datos YAML)

1. Definir esquema de tablas YAML para tareas/proyectos/calendario y tiempo.
2. Crear modulo de repositorio (CRUD) para esas tablas.
3. Integrar alta de tarea con asignacion a hoy/semana/mes.
4. Regenerar bitacora para reflejar nuevas tareas del dia.

Ver detalle en docs/PLAN_YAML_RELACIONAL.md.

## Restricciones y criterios de calidad

- Mantener compatibilidad con el flujo actual de bitacoras.
- Cambios pequenos y testeables; no mezclar refactor masivo con nuevas features.
- Toda tarea marcada como resuelta debe tener evidencia en codigo y validacion ejecutable.

## Checklist operativo para arrancar

- Ejecutar smoke test CLI:
  - c:/Projects/brackets-workspace/brackets/.venv/Scripts/python.exe -m brackets.main --help
- Ejecutar tests parser:
  - c:/Projects/brackets-workspace/brackets/.venv/Scripts/python.exe brackets/tests/test_utils_content_parser.py
- Revisar backlog y marcar objetivo de la sesion (maximo 1 bloque funcional).

## Prompt sugerido para iniciar un nuevo chat

"Lee docs/HANDOFF_AGENTE_SIGUIENTE.md, docs/BACKLOG_UNIFICADO.md y docs/PLAN_YAML_RELACIONAL.md. Retoma desde el siguiente bloque WIP (modularizar main.py en piezas testeables), manteniendo commits pequenos y actualizando este handoff tras cada bloque cerrado con evidencia de test."
