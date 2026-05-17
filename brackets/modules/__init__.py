"""Módulo de funcionalidades específicas - Proyectos, aprendizaje, etc."""

# Placeholder para futuras funcionalidades (FASE 3+)
# from brackets.modules.holidays import HolidayManager
# from brackets.modules.projects import ProjectManager
# from brackets.modules.learning import LearningManager

from brackets.modules.pomodoro_timer import (
	TimerConfig,
	PomodoroTimerEngine,
	PomodoroConsoleApp,
	run_pomodoro_standalone,
)

__all__ = [
	"TimerConfig",
	"PomodoroTimerEngine",
	"PomodoroConsoleApp",
	"run_pomodoro_standalone",
]
