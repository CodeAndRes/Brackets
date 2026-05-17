#!/usr/bin/env python3
"""Pomodoro timer para Brackets (v1).

Incluye:
- Motor de estado testeable (sin I/O directo).
- UI de consola con barra de progreso y personaje parpadeante.
- Configuración YAML para foco/descanso/jornada.
- Hook de integración para registrar sesiones finalizadas.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
import os
import time
from typing import Callable, Dict, Optional

import yaml


DEFAULT_CONFIG_FILENAME = "pomodoro_timer.yaml"


@dataclass
class TimerConfig:
    """Configuración del timer en minutos/segundos de refresco."""

    focus_minutes: int = 25
    break_minutes: int = 5
    workday_minutes: int = 420
    progress_bar_width: int = 24
    tick_seconds: int = 1
    avatar_open: str = "(^_^)"
    avatar_closed: str = "(-_-)"

    @property
    def focus_seconds(self) -> int:
        return max(1, int(self.focus_minutes) * 60)

    @property
    def break_seconds(self) -> int:
        return max(1, int(self.break_minutes) * 60)

    @property
    def workday_seconds(self) -> int:
        return max(1, int(self.workday_minutes) * 60)

    def to_dict(self) -> Dict[str, int]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict) -> "TimerConfig":
        if not isinstance(payload, dict):
            return cls()

        default = cls()
        return cls(
            focus_minutes=int(payload.get("focus_minutes", default.focus_minutes)),
            break_minutes=int(payload.get("break_minutes", default.break_minutes)),
            workday_minutes=int(payload.get("workday_minutes", default.workday_minutes)),
            progress_bar_width=int(payload.get("progress_bar_width", default.progress_bar_width)),
            tick_seconds=int(payload.get("tick_seconds", default.tick_seconds)),
            avatar_open=str(payload.get("avatar_open", default.avatar_open)),
            avatar_closed=str(payload.get("avatar_closed", default.avatar_closed)),
        )


def _default_data_dir(base_dir: str) -> str:
    candidate = os.path.join(os.path.abspath(base_dir), "data")
    if os.path.isdir(candidate):
        return candidate
    return os.path.abspath(base_dir)


def load_timer_config(base_dir: str = ".") -> tuple[TimerConfig, str]:
    """Carga configuración de timer desde YAML. Si no existe, usa defaults."""

    data_dir = _default_data_dir(base_dir)
    config_path = os.path.join(data_dir, DEFAULT_CONFIG_FILENAME)

    if not os.path.exists(config_path):
        return TimerConfig(), config_path

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            payload = yaml.safe_load(f) or {}
        return TimerConfig.from_dict(payload), config_path
    except Exception:
        return TimerConfig(), config_path


def save_timer_config(config: TimerConfig, config_path: str) -> None:
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config.to_dict(), f, sort_keys=False, allow_unicode=True)


class PomodoroTimerEngine:
    """Motor del timer (sin dependencia de consola)."""

    def __init__(self, config: TimerConfig):
        self.config = config
        self.phase: str = "idle"
        self.is_running: bool = False
        self.is_paused: bool = False
        self.remaining_seconds: int = 0
        self.phase_total_seconds: int = 0
        self.completed_focus_sessions: int = 0
        self.worked_seconds_today: int = 0
        self.blink_open: bool = True
        self.last_event: Optional[str] = None
        self.last_session_record: Optional[Dict] = None
        self._session_start_ts: Optional[str] = None
        self._on_session_completed: Optional[Callable[[Dict], None]] = None

    def set_session_completed_hook(self, callback: Optional[Callable[[Dict], None]]) -> None:
        """Hook de extensión para integración futura con notas/tareas."""
        self._on_session_completed = callback

    def start_focus(self) -> None:
        self.phase = "focus"
        self.phase_total_seconds = self.config.focus_seconds
        self.remaining_seconds = self.phase_total_seconds
        self.is_running = True
        self.is_paused = False
        self.last_event = "focus_started"
        self._session_start_ts = datetime.utcnow().isoformat() + "Z"

    def start_break(self) -> None:
        self.phase = "break"
        self.phase_total_seconds = self.config.break_seconds
        self.remaining_seconds = self.phase_total_seconds
        self.is_running = True
        self.is_paused = False
        self.last_event = "break_started"
        self._session_start_ts = datetime.utcnow().isoformat() + "Z"

    def pause(self) -> None:
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.last_event = "paused"

    def resume(self) -> None:
        if self.is_running and self.is_paused:
            self.is_paused = False
            self.last_event = "resumed"

    def reset(self) -> None:
        self.phase = "idle"
        self.is_running = False
        self.is_paused = False
        self.remaining_seconds = 0
        self.phase_total_seconds = 0
        self.last_event = "reset"
        self._session_start_ts = None

    def tick(self, seconds: int = 1) -> Optional[str]:
        """Avanza el temporizador. Devuelve evento si terminó fase."""
        if not self.is_running or self.is_paused:
            return None

        step = max(1, int(seconds))
        self.remaining_seconds = max(0, self.remaining_seconds - step)
        self.blink_open = not self.blink_open

        if self.remaining_seconds > 0:
            return None

        # Fin de fase
        self.is_running = False
        self.is_paused = False
        event = f"{self.phase}_finished"
        self.last_event = event

        if self.phase == "focus":
            self.completed_focus_sessions += 1
            self.worked_seconds_today += self.config.focus_seconds

        self.last_session_record = {
            "phase": self.phase,
            "started_at": self._session_start_ts,
            "ended_at": datetime.utcnow().isoformat() + "Z",
            "planned_seconds": self.phase_total_seconds,
            "workday_progress": round(self.workday_progress(), 4),
        }

        if self.phase == "focus" and self._on_session_completed:
            self._on_session_completed(self.last_session_record)

        return event

    def progress(self) -> float:
        if self.phase_total_seconds <= 0:
            return 0.0
        completed = self.phase_total_seconds - self.remaining_seconds
        return max(0.0, min(1.0, completed / self.phase_total_seconds))

    def workday_progress(self) -> float:
        return max(0.0, min(1.0, self.worked_seconds_today / self.config.workday_seconds))

    def phase_label(self) -> str:
        if self.phase == "focus":
            return "FOCUS"
        if self.phase == "break":
            return "BREAK"
        return "IDLE"

    def avatar(self) -> str:
        return self.config.avatar_open if self.blink_open else self.config.avatar_closed

    def remaining_hhmmss(self) -> str:
        minutes, seconds = divmod(self.remaining_seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"


class PomodoroConsoleApp:
    """Interfaz de consola para usar el timer."""

    def __init__(self, base_dir: str = "."):
        self.config, self.config_path = load_timer_config(base_dir)
        self.engine = PomodoroTimerEngine(self.config)
        self.engine.set_session_completed_hook(self._register_session)
        self.session_log = []

    def _register_session(self, record: Dict) -> None:
        # Hook de extensión para futura integración con notas/tasks.
        self.session_log.append(record)

    def _progress_bar(self) -> str:
        width = max(8, self.config.progress_bar_width)
        ratio = self.engine.progress()
        completed = int(width * ratio)
        bar = "#" * completed + "-" * (width - completed)
        return f"[{bar}] {int(ratio * 100):3d}%"

    def _render_status_line(self) -> str:
        return (
            f"{self.engine.avatar()} {self.engine.phase_label()} "
            f"{self._progress_bar()} ⏱ {self.engine.remaining_hhmmss()}"
        )

    def _notify_phase_end(self, event: str) -> None:
        print("\a", end="")
        if event == "focus_finished":
            print("\n✅ Sesión de foco finalizada.")
        elif event == "break_finished":
            print("\n☕ Descanso finalizado.")

    def _run_phase(self, phase: str) -> Optional[str]:
        if phase == "focus":
            self.engine.start_focus()
        else:
            self.engine.start_break()

        event = None
        try:
            while self.engine.is_running:
                print("\r" + self._render_status_line(), end="", flush=True)
                time.sleep(max(1, self.config.tick_seconds))
                event = self.engine.tick(self.config.tick_seconds)
            print()
        except KeyboardInterrupt:
            self.engine.pause()
            print("\n⏸ Sesión pausada por usuario (Ctrl+C).")
            return "paused"

        if event:
            self._notify_phase_end(event)
        return event

    def _show_summary(self) -> None:
        progress = int(self.engine.workday_progress() * 100)
        worked_minutes = self.engine.worked_seconds_today // 60
        print("\n📊 RESUMEN DE JORNADA")
        print("-" * 36)
        print(f"Sesiones foco completadas: {self.engine.completed_focus_sessions}")
        print(f"Tiempo de foco acumulado: {worked_minutes} min")
        print(f"Progreso jornada: {progress}%")
        if self.session_log:
            print(f"Último registro: {self.session_log[-1]}")

    def _configure(self) -> None:
        print("\n⚙️ CONFIGURAR TIMER")
        print("(Enter mantiene valor actual)")

        def ask_int(label: str, current: int) -> int:
            raw = input(f"{label} [{current}]: ").strip()
            if not raw:
                return current
            try:
                value = int(raw)
                return max(1, value)
            except ValueError:
                print("Valor inválido, se mantiene el actual.")
                return current

        self.config.focus_minutes = ask_int("Minutos foco", self.config.focus_minutes)
        self.config.break_minutes = ask_int("Minutos descanso", self.config.break_minutes)
        self.config.workday_minutes = ask_int("Minutos jornada", self.config.workday_minutes)
        self.config.progress_bar_width = ask_int("Ancho barra progreso", self.config.progress_bar_width)
        self.config.tick_seconds = ask_int("Refresco en segundos", self.config.tick_seconds)

        avatar_open = input(f"Avatar ojos abiertos [{self.config.avatar_open}]: ").strip()
        avatar_closed = input(f"Avatar parpadeo [{self.config.avatar_closed}]: ").strip()
        if avatar_open:
            self.config.avatar_open = avatar_open
        if avatar_closed:
            self.config.avatar_closed = avatar_closed

        save_timer_config(self.config, self.config_path)
        self.engine.config = self.config
        print(f"✅ Configuración guardada en: {self.config_path}")

    def run_menu(self) -> None:
        while True:
            print("\n⏲️ POMODORO TIMER")
            print("=" * 36)
            print("1. ▶️ Iniciar sesión de foco")
            print("2. ⏸ Pausar sesión actual")
            print("3. ▶️ Reanudar sesión pausada")
            print("4. ♻️ Reset sesión actual")
            print("5. ⚙️ Configurar timer")
            print("6. 📊 Ver resumen")
            print("0. ↩️ Salir")

            choice = input("Opción: ").strip()

            if choice == "1":
                event = self._run_phase("focus")
                if event == "focus_finished":
                    auto_break = input("¿Iniciar descanso ahora? (s/n): ").strip().lower()
                    if auto_break in ("s", "si", "y", "yes"):
                        self._run_phase("break")
            elif choice == "2":
                self.engine.pause()
                print("⏸ Timer pausado.")
            elif choice == "3":
                if self.engine.is_paused:
                    self.engine.resume()
                    resumed_phase = self.engine.phase if self.engine.phase in ("focus", "break") else "focus"
                    self._run_phase(resumed_phase)
                else:
                    print("ℹ️ No hay sesión pausada.")
            elif choice == "4":
                self.engine.reset()
                print("♻️ Sesión reseteada.")
            elif choice == "5":
                self._configure()
            elif choice == "6":
                self._show_summary()
            elif choice == "0":
                print("👋 Saliendo del timer.")
                break
            else:
                print("❌ Opción inválida")


def run_pomodoro_standalone(base_dir: str = ".") -> None:
    """Punto de entrada reutilizable para menú Brackets y modo standalone."""
    app = PomodoroConsoleApp(base_dir=base_dir)
    app.run_menu()


if __name__ == "__main__":
    run_pomodoro_standalone()
