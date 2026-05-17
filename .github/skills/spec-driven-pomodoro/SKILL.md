---
name: spec-driven-pomodoro
description: "Workflow SDD para diseñar, implementar y validar el módulo Pomodoro de Brackets con trazabilidad a spec y criterios de aceptación."
argument-hint: "Describe el alcance o cambio del módulo Pomodoro"
---

# Spec-Driven Pomodoro

## Cuando usar

- Nueva funcionalidad del timer.
- Cambio de comportamiento de sesión/descanso.
- Integración con menú/CLI de Brackets.

## Procedimiento

1. Actualizar `docs/pomodoro_spec_v1.md` con cambios y criterios verificables.
2. Implementar en código con referencia explícita al spec en commits/PR.
3. Crear o actualizar pruebas unitarias.
4. Validar criterios y documentar resultados en `docs/pomodoro_implementation_report.md`.

## Regla de oro

No se implementa nada fuera del alcance de spec sin confirmación del usuario.
