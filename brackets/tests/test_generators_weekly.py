#!/usr/bin/env python3
"""
Tests unitarios para WeeklyGenerator en generators/weekly.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from brackets.generators.weekly import WeeklyGenerator


class TestWeeklyGenerator:
    """Tests para la clase WeeklyGenerator."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.generator = WeeklyGenerator(directory='.')

    def test_iso_next_week_dates_real_case_week12_2026(self):
        """Reproduce el caso real: Week12/2026 debe avanzar a días 23-27 de marzo."""
        try:
            dates = self.generator._calculate_next_week_dates_iso(2026, 12)

            assert len(dates) == 5, f"Debería devolver 5 días, devolvió {len(dates)}"
            assert [d.day for d in dates] == [23, 24, 25, 26, 27], f"Días incorrectos: {[d.day for d in dates]}"
            assert all(d.month == 3 for d in dates), f"Mes incorrecto en fechas: {[d.month for d in dates]}"

            print("✅ Test: Week12/2026 avanza a 23-27 marzo")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test Week12/2026 falló: {e}")
            self.failed += 1

    def test_iso_next_week_always_monday_to_friday(self):
        """Valida que siempre genere lunes-viernes consecutivos."""
        try:
            dates = self.generator._calculate_next_week_dates_iso(2026, 1)

            assert len(dates) == 5, f"Debería devolver 5 días, devolvió {len(dates)}"
            assert [d.weekday() for d in dates] == [0, 1, 2, 3, 4], (
                f"No es lunes-viernes: {[d.weekday() for d in dates]}"
            )

            print("✅ Test: siempre genera lunes-viernes")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test lunes-viernes falló: {e}")
            self.failed += 1

    def test_create_next_or_manual_fallback_when_no_recent_weekly(self):
        """Si no hay bitácora previa, debe usar flujo manual automáticamente."""
        try:
            self.generator.finder.get_most_recent_weekly = lambda: None
            self.generator.create_manual_weekly_bitacora = lambda: True

            result = self.generator.create_next_or_manual_weekly_bitacora()
            assert result is True, "Debería retornar éxito al completar flujo manual"

            print("✅ Test: fallback a manual cuando no hay bitácora previa")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test fallback manual falló: {e}")
            self.failed += 1

    def test_create_next_or_manual_prefers_automatic_when_recent_exists(self):
        """Si hay bitácora previa, debe ejecutar el flujo automático."""
        try:
            calls = {"auto": 0, "manual": 0}

            self.generator.finder.get_most_recent_weekly = lambda: "fake_weekly.md"

            def fake_auto(ask_for_weight: bool = True):
                calls["auto"] += 1
                return True

            def fake_manual():
                calls["manual"] += 1
                return True

            self.generator.create_next_weekly_bitacora = fake_auto
            self.generator.create_manual_weekly_bitacora = fake_manual

            result = self.generator.create_next_or_manual_weekly_bitacora()
            assert result is True, "Debería retornar éxito en flujo automático"
            assert calls["auto"] == 1, f"Flujo automático esperado 1 vez, obtuvo {calls['auto']}"
            assert calls["manual"] == 0, f"Flujo manual no debería ejecutarse, obtuvo {calls['manual']}"

            print("✅ Test: flujo automático preferido cuando hay base previa")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test preferencia automática falló: {e}")
            self.failed += 1

    def run_all(self):
        """Ejecutar todos los tests."""
        print("\n🧪 TESTS: generators/weekly.py")
        print("=" * 50)

        self.test_iso_next_week_dates_real_case_week12_2026()
        self.test_iso_next_week_always_monday_to_friday()
        self.test_create_next_or_manual_fallback_when_no_recent_weekly()
        self.test_create_next_or_manual_prefers_automatic_when_recent_exists()

        print(f"\n📊 Resultado: ✅ {self.passed} | ❌ {self.failed}")
        return self.failed == 0


if __name__ == "__main__":
    tester = TestWeeklyGenerator()
    success = tester.run_all()
    sys.exit(0 if success else 1)
