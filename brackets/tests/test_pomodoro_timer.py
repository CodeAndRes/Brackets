#!/usr/bin/env python3
"""Tests básicos del módulo pomodoro_timer."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from brackets.modules.pomodoro_timer import TimerConfig, PomodoroTimerEngine


class TestPomodoroTimer:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def _ok(self, name: str):
        print(f"✅ Test: {name}")
        self.passed += 1

    def _fail(self, name: str, error: Exception):
        print(f"❌ Test {name} falló: {error}")
        self.failed += 1

    def test_start_pause_resume_reset(self):
        name = "start/pause/resume/reset"
        try:
            cfg = TimerConfig(focus_minutes=1, break_minutes=1, workday_minutes=10)
            engine = PomodoroTimerEngine(cfg)

            engine.start_focus()
            assert engine.is_running is True
            assert engine.phase == "focus"

            engine.pause()
            assert engine.is_paused is True

            engine.resume()
            assert engine.is_paused is False

            engine.reset()
            assert engine.phase == "idle"
            assert engine.is_running is False
            assert engine.remaining_seconds == 0
            self._ok(name)
        except Exception as e:
            self._fail(name, e)

    def test_tick_and_finish_focus(self):
        name = "tick finaliza foco"
        try:
            cfg = TimerConfig(focus_minutes=1, break_minutes=1, workday_minutes=10)
            engine = PomodoroTimerEngine(cfg)
            events = []
            engine.set_session_completed_hook(lambda rec: events.append(rec))

            engine.start_focus()
            for _ in range(60):
                event = engine.tick(1)

            assert event == "focus_finished"
            assert engine.completed_focus_sessions == 1
            assert len(events) == 1
            assert events[0]["phase"] == "focus"
            self._ok(name)
        except Exception as e:
            self._fail(name, e)

    def test_progress_bounds(self):
        name = "progress en rango"
        try:
            cfg = TimerConfig(focus_minutes=1, break_minutes=1, workday_minutes=2)
            engine = PomodoroTimerEngine(cfg)

            engine.start_focus()
            p0 = engine.progress()
            assert 0.0 <= p0 <= 1.0

            for _ in range(30):
                engine.tick(1)
            p1 = engine.progress()
            assert p1 > p0
            assert 0.0 <= p1 <= 1.0
            self._ok(name)
        except Exception as e:
            self._fail(name, e)

    def run_all(self):
        print("\n🧪 TESTS: modules/pomodoro_timer.py")
        print("=" * 50)
        self.test_start_pause_resume_reset()
        self.test_tick_and_finish_focus()
        self.test_progress_bounds()
        print(f"\n📊 Resultado: ✅ {self.passed} | ❌ {self.failed}")
        return self.failed == 0


if __name__ == "__main__":
    tester = TestPomodoroTimer()
    success = tester.run_all()
    sys.exit(0 if success else 1)
