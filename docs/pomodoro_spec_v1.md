# Pomodoro Timer Spec v1

Fecha: 2026-04-03
Estado: aprobado para implementación v1

## 1. Objetivo
Crear un módulo Pomodoro reutilizable en Brackets que pueda ejecutarse:
- como módulo independiente,
- y como opción integrada en el menú principal.

## 2. Requisitos funcionales

### 2.1 Control básico del timer
El sistema debe permitir:
- iniciar sesión de foco,
- pausar,
- reanudar,
- resetear,
- iniciar descanso.

### 2.2 Visualización en consola
Durante foco/descanso debe mostrar:
- barra de progreso,
- tiempo restante,
- personaje con parpadeo (animación simple por alternancia).

### 2.3 Configuración
Debe soportar configuración editable de:
- duración de sesión de foco (minutos),
- duración de descanso (minutos),
- duración de jornada (minutos objetivo diarios),
- ancho de barra de progreso,
- intervalo de refresco.

### 2.4 Notificación de fin
Al terminar una sesión de foco o descanso, el sistema debe emitir notificación visible en consola (y beep ASCII cuando sea posible).

### 2.5 Ejecución dual
Debe poder ejecutarse:
- standalone (`python -m brackets.modules.pomodoro_timer`),
- desde Brackets menú de herramientas.

### 2.6 Preparación para integración con notas
Debe existir un punto de extensión (hook) para registrar sesión finalizada y facilitar integración futura con documentos de notas.

## 3. Requisitos no funcionales

### 3.1 Precisión
Deriva máxima esperada por sesión <= 1 segundo por minuto en modo estándar de consola.

### 3.2 Consumo
No usar bucles ocupados (busy waiting). Refresco con `sleep` configurable.

### 3.3 Trazabilidad
Cada sesión de foco finalizada debe poder registrarse en memoria del proceso y exportarse a estructura serializable.

### 3.4 Mantenibilidad
Separar lógica del temporizador (motor) de la UI de consola para facilitar testing.

## 4. Interfaz esperada

## 4.1 API Python

- `TimerConfig`: dataclass de parámetros.
- `PomodoroTimerEngine`: estado y transiciones (`start_focus`, `start_break`, `pause`, `resume`, `reset`, `tick`).
- `PomodoroConsoleApp`: ejecución interactiva (`run_menu`, `run_focus_session`).

### 4.2 Ejemplo de uso (API)

```python
from brackets.modules.pomodoro_timer import TimerConfig, PomodoroTimerEngine

cfg = TimerConfig(focus_minutes=25, break_minutes=5, workday_minutes=420)
engine = PomodoroTimerEngine(cfg)
engine.start_focus()
while engine.is_running:
    engine.tick(1)
```

### 4.3 Ejemplo de uso (standalone)

```bash
python -m brackets.modules.pomodoro_timer
```

## 5. Criterios de aceptación

CA-01: El motor permite iniciar/pausar/reanudar/resetear sin excepciones.
CA-02: `tick` reduce segundos restantes y marca fin de fase en el momento esperado.
CA-03: La consola muestra barra de progreso y personaje parpadeante durante ejecución.
CA-04: Existe configuración de foco/descanso/jornada configurable por archivo YAML.
CA-05: El módulo se ejecuta standalone y también desde menú de Brackets.
CA-06: Se incluye prueba unitaria básica para transiciones del motor.
CA-07: Existe hook de integración para registrar sesiones completadas.

## 6. Fuera de alcance en v1
- Sincronización bidireccional completa con tareas Markdown/YAML.
- Tracking multiusuario.
- App móvil.
- Persistencia histórica avanzada por vault (se deja preparado el hook).
