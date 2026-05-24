# Plan de Arquitectura: Modelo Relacional en YAML

Fecha: 2026-05-24
Estado: plan base para ejecucion incremental

## Objetivo

Implementar un modelo de datos relacional persistido en archivos YAML para gestionar trabajo (tareas/notas/tiempo), y usar Markdown como salida renderizada.

## Principios de diseno

- Fuente de verdad: YAML estructurado (tablas).
- Markdown: materializacion de lectura, no fuente primaria.
- IDs estables para entidades y referencias FK.
- Operaciones idempotentes (re-render sin duplicados).

## Tablas YAML propuestas

Se sugiere una carpeta nueva: data/workdb/

- projects.yaml
- tasks.yaml
- months.yaml
- weeks.yaml
- days.yaml
- time_entries.yaml
- notes.yaml
- task_links.yaml

## Esquema minimo por tabla

### projects.yaml
- id (PK)
- code (unico)
- name
- status
- created_at

### tasks.yaml
- id (PK)
- project_id (FK -> projects.id)
- title
- description
- status (todo, doing, done, blocked)
- priority
- due_scope (day, week, month, backlog)
- due_day_id (FK opcional -> days.id)
- due_week_id (FK opcional -> weeks.id)
- due_month_id (FK opcional -> months.id)
- created_at
- updated_at

### months.yaml
- id (PK)
- year
- month
- label

### weeks.yaml
- id (PK)
- year
- iso_week
- month_id (FK -> months.id)

### days.yaml
- id (PK)
- date (YYYY-MM-DD)
- week_id (FK -> weeks.id)
- weekday

### time_entries.yaml
- id (PK)
- task_id (FK -> tasks.id)
- started_at
- ended_at
- seconds
- state (running, paused, closed)

### notes.yaml
- id (PK)
- task_id (FK opcional -> tasks.id)
- day_id (FK opcional -> days.id)
- content
- created_at

### task_links.yaml
- id (PK)
- from_task_id (FK -> tasks.id)
- to_task_id (FK -> tasks.id)
- relation_type (blocks, related, duplicate)

## Flujo funcional objetivo

### Crear tarea
1. Usuario abre comando crear tarea.
2. Sistema lista proyectos.
3. Usuario elige proyecto y alcance temporal (hoy/semana/mes/luego).
4. Se inserta task con FK al periodo correspondiente.
5. Si alcance=hoy, opcion de regenerar bitacora del dia.

### Trabajo en tarea + tiempo
1. Usuario elige tarea activa.
2. Start: crea time_entry en running.
3. Pause: cierra parcial y deja estado pausado.
4. Resume: abre nueva entrada running para la misma tarea.
5. Stop: cierra entrada y actualiza acumulados.

### Render de Markdown
1. Leer tablas YAML.
2. Construir vista por semana/dia/proyecto.
3. Renderizar .md usando plantilla declarada en YAML.
4. Escribir archivo final sin perder contenido manual protegido por marcadores.

## Estructura de modulos recomendada

- brackets/workdb/models.py
- brackets/workdb/repository.py
- brackets/workdb/validators.py
- brackets/workdb/service.py
- brackets/workdb/render_md.py
- brackets/workdb/migrations.py

## MVP recomendado (arrancable ya)

### Bloque 1 (base)
- Crear tablas: projects.yaml, tasks.yaml, weeks.yaml, days.yaml.
- Crear repositorio CRUD minimo.
- Crear comando: alta de tarea con asignacion a proyecto y scope day/week/month.

### Bloque 2 (integracion bitacora)
- Resolver day/week actual.
- Generar/actualizar seccion de tareas en bitacora diaria/semanal.
- Opcion de regeneracion para el mismo dia.

### Bloque 3 (tiempo)
- Integrar time_entries.yaml con start/pause/resume/stop asociado a task_id.

## Pruebas minimas por bloque

- Test de integridad de FKs (no insertar task con project_id inexistente).
- Test de idempotencia de render (dos renders seguidos = mismo resultado).
- Test de flujo start/pause/resume/stop en time_entries.

## Decisiones abiertas (requieren validacion de usuario)

- Formato de IDs (uuid vs secuencial legible).
- Regla de conflicto cuando una tarea tiene day_id y week_id simultaneamente.
- Estrategia de preservacion de texto manual en archivos .md renderizados.
- Nivel de detalle de estados de tarea (simple vs avanzado).

## Comando objetivo final (vision)

- brackets task add
- brackets task start <task_id>
- brackets task pause <task_id>
- brackets task resume <task_id>
- brackets task stop <task_id>
- brackets bitacora regenerate --day YYYY-MM-DD
