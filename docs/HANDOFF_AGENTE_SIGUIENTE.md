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

## Pendientes tecnicos criticos (confirmados)

- Fallback automatico a flujo manual cuando no existen bitacoras previas.
- Formato de titulo mensual esperado (objetivo: '# July Topics ☀️').
- Unificar versionado (setup.py vs modulos internos).
- Politica de visibilidad de vaults (local vs root).

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

"Lee docs/HANDOFF_AGENTE_SIGUIENTE.md, docs/BACKLOG_UNIFICADO.md y docs/PLAN_YAML_RELACIONAL.md. Necesito que ejecutes el siguiente bloque del MVP de base de datos YAML para tareas/proyectos y dejes pruebas minimas."
