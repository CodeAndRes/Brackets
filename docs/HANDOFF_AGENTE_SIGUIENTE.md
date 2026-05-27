# Handoff Maestro para Siguiente Agente

Fecha: 2026-05-26
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

Fecha de corte: 2026-05-26

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
- Bloque correctivo: guardrail para contexto CLI (flags requieren vault local o --directory, y --directory debe apuntar a vault con data/config.yaml).
  - Evidencia: brackets/core/vault_selection.py, brackets/tests/test_core_vault_selection.py.
- Bloque correctivo: validacion final en startup para impedir crear manager sobre directorios no-vault (corta antes de run/dispatch).
  - Evidencia: brackets/core/startup.py, brackets/tests/test_core_startup.py.
- Bloque correctivo critico: fix de ruta en creacion semanal automatica (evita escribir en cwd/workspace root).
  - Causa raiz: `create_next_weekly_bitacora` generaba filename sin `directory`, cayendo a directorio de ejecucion.
  - Evidencia: brackets/generators/weekly.py (usa `generate_filename(..., directory=self.directory)`), brackets/tests/test_generators_weekly.py.
  - Validacion: suite completa `77/77` OK + prueba E2E real desde `C:/Projects` con `./brackets_quickstart.ps1` (selector `MyJobNotes`, quick-key `n`) creando `C:/Projects/brackets-workspace/MyJobNotes/[2026][06]Week23.md`.
- Bloque correctivo de seguridad: rutas de plantilla semanal/mensual deshabilitadas explícitamente con excepción controlada.
  - Objetivo: evitar fallos ambiguos (`NameError`) o retornos silenciosos en flujos aún no soportados.
  - Evidencia: brackets/generators/weekly.py (`create_weekly_from_template`), brackets/generators/monthly.py (`create_monthly_from_template`).
  - Validacion: tests nuevos en brackets/tests/test_generators_weekly.py y brackets/tests/test_generators_monthly.py + suite completa `80/80` OK.
- Bloque preventivo: smoke E2E de scope de rutas (root vs vault local) para semanal y mensual.
  - Objetivo: detectar regresiones de escritura en cwd/workspace root antes de llegar a usuario final.
  - Evidencia: brackets/tests/test_path_scope_smoke.py + integración en brackets/tests/test_suite.py.
  - Validacion: test dedicado `python -m brackets.tests.test_path_scope_smoke` + suite completa `82/82` OK.
- Bloque de modularización: eliminación de flujo legacy `handle_debug_tools` en main para dejar `ToolsController` como única implementación de herramientas/debug.
  - Objetivo: reducir duplicidad de rutas y evitar drift entre menús legacy y YAML.
  - Evidencia: limpieza en brackets/main.py (imports legacy removidos + método legacy eliminado), comportamiento mantenido vía brackets/core/tools_controller.py.
  - Validacion: `python -m brackets.tests.test_core_tools_controller` + suite completa `82/82` OK.
- Bloque funcional: visibilidad por tipo de vault (work/personal) con reglas finas en menú.
  - Objetivo: habilitar reglas de visibilidad sin duplicar menús por vault.
  - Evidencia: `BitacoraManager` expone `vault_type` y contexto `vault_type_work`/`vault_type_personal`; `data/menu_config.yaml` aplica `context_tag: vault_type_work` a `tool_pomodoro`.
  - Tests: nuevo `brackets/tests/test_core_vault_type_menu_visibility.py` + integración en `brackets/tests/test_suite.py`.
  - Validacion: suite completa `85/85` OK.
- Bloque correctivo preventivo: fix espejo de ruta en creacion mensual automatica (mismo patron de riesgo que semanal).
  - Causa raiz: `create_next_monthly_topics` generaba filename sin `directory`, potencialmente escribiendo en cwd.
  - Evidencia: brackets/generators/monthly.py (usa `generate_filename(..., directory=self.directory)`), brackets/tests/test_generators_monthly.py.
  - Validacion: test focal mensual OK + suite completa `78/78` OK.

## Postmortem corto: por que costo tanto encontrar este bug

- Sintoma observable engañoso: el menu mostraba vault correcto (`MyJobNotes`), pero la escritura real ocurria en el cwd por una llamada interna sin `directory`.
- Señal tardia: se reforzaron capas de seleccion/startup antes de inspeccionar la capa final de IO (generacion de filename + write).
- Cobertura incompleta inicial: habia tests de seleccion de vault y startup, pero faltaba test de integracion para ruta final de archivo en flujo automatico semanal.
- Reproduccion parcial al inicio: validar por flags o tests unitarios no replico inmediatamente el flujo exacto del usuario (`PS C:/Projects > ./brackets_quickstart.ps1` + quick-key `n`).

## Protocolo obligatorio para evitar repeticion

1. Reproducir primero en flujo real del usuario antes de hipotetizar arquitectura.
2. Trazar la ruta de destino extremo a extremo: seleccion de vault -> manager.directory -> generate_filename -> confirm_overwrite -> safe_file_write.
3. Ante bug de ubicacion, inspeccionar primero la ultima capa de IO (path final) y luego subir de capa.
4. No cerrar un fix sin prueba E2E en el entrypoint real y sin test automatizado de regresion en la capa donde ocurrio la fuga.
5. Si la UI reporta una ruta logica y el filesystem no coincide, priorizar instrumentacion/validacion de path efectivo sobre cambios de guardrails adicionales.

## Checklist anti-regresion (bugs de ruta)

- [ ] Cada llamada a `generate_filename` explicita `directory`.
- [ ] El test de regresion valida existencia fisica del archivo en el vault esperado (no solo mocks de flujo).
- [ ] Se valida en ejecucion desde workspace root (`C:/Projects`) y desde vault local.
- [ ] Se verifica que no aparezcan archivos espejo en root tras crear semanal.

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
- Ultimo objetivo tecnico incremental: guardrail de contexto CLI y validacion estricta de --directory como vault root.
- Ultimo objetivo tecnico incremental: validacion de vault root tambien en startup (defensa en profundidad).
- Ultimo objetivo tecnico incremental: fix definitivo de escritura semanal automatica dentro del vault seleccionado (no en workspace root/cwd).
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
