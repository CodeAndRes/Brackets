#!/usr/bin/env python3
"""
Tests para brackets/worklog/event_log.py
"""

import os
import sys
import tempfile
import shutil
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from brackets.worklog.event_log import EventLog


class TestEventLog:
    """Tests para EventLog."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.temp_dir = None

    def setup(self):
        """Crea un directorio temporal como vault."""
        self.temp_dir = tempfile.mkdtemp(prefix="brackets_test_")
        return EventLog(self.temp_dir)

    def teardown(self):
        """Limpia el directorio temporal."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        self.temp_dir = None

    def test_append_creates_file(self):
        """Test que append crea el archivo de log del día."""
        try:
            log = self.setup()
            entry = log.append("test_event", detail="hello")

            assert entry["event"] == "test_event"
            assert entry["detail"] == "hello"
            assert "ts" in entry

            # Verificar que el archivo existe
            today_file = log._day_path(date.today())
            assert os.path.exists(today_file), "El archivo de log debería existir"

            print("✅ Test: append crea archivo y devuelve entry correcto")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test append_creates_file falló: {e}")
            self.failed += 1
        finally:
            self.teardown()

    def test_append_multiple_entries(self):
        """Test que append acumula entries en el mismo archivo."""
        try:
            log = self.setup()
            log.append("event_1", seq=1)
            log.append("event_2", seq=2)
            log.append("event_3", seq=3)

            entries = log.read_day()
            assert len(entries) == 3, f"Esperaba 3 entries, obtuvo {len(entries)}"
            assert entries[0]["event"] == "event_1"
            assert entries[2]["seq"] == 3

            print("✅ Test: append acumula múltiples entries")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test append_multiple_entries falló: {e}")
            self.failed += 1
        finally:
            self.teardown()

    def test_read_day_empty(self):
        """Test que read_day devuelve lista vacía si no hay archivo."""
        try:
            log = self.setup()
            entries = log.read_day(date(2020, 1, 1))
            assert entries == [], f"Esperaba lista vacía, obtuvo {entries}"

            print("✅ Test: read_day devuelve vacío para día sin log")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test read_day_empty falló: {e}")
            self.failed += 1
        finally:
            self.teardown()

    def test_read_day_today(self):
        """Test que read_day(None) lee el día actual."""
        try:
            log = self.setup()
            log.append("session_start")
            entries = log.read_day()  # None = today
            assert len(entries) == 1
            assert entries[0]["event"] == "session_start"

            print("✅ Test: read_day() lee el día actual")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test read_day_today falló: {e}")
            self.failed += 1
        finally:
            self.teardown()

    def test_read_range(self):
        """Test que read_range combina entries de varios días."""
        try:
            log = self.setup()
            log._ensure_dir()

            # Crear manualmente archivos para días consecutivos
            import yaml
            for i in range(3):
                day = date(2026, 3, 10 + i)
                path = log._day_path(day)
                data = {"entries": [{"ts": f"2026-03-{10+i}T09:00:00", "event": f"day_{i}"}]}
                with open(path, "w", encoding="utf-8") as f:
                    yaml.dump(data, f, allow_unicode=True)

            entries = log.read_range(date(2026, 3, 10), date(2026, 3, 12))
            assert len(entries) == 3, f"Esperaba 3 entries, obtuvo {len(entries)}"
            assert entries[0]["event"] == "day_0"
            assert entries[2]["event"] == "day_2"

            print("✅ Test: read_range combina entries de varios días")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test read_range falló: {e}")
            self.failed += 1
        finally:
            self.teardown()

    def test_corrupted_file_returns_empty(self):
        """Test que un archivo corrupto no rompe la lectura."""
        try:
            log = self.setup()
            log._ensure_dir()

            # Escribir contenido inválido
            path = log._day_path(date(2026, 1, 1))
            with open(path, "w", encoding="utf-8") as f:
                f.write("{{invalid yaml: [[[")

            entries = log.read_day(date(2026, 1, 1))
            assert entries == [], "Archivo corrupto debería devolver lista vacía"

            print("✅ Test: archivo corrupto devuelve lista vacía")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test corrupted_file falló: {e}")
            self.failed += 1
        finally:
            self.teardown()

    def test_entry_preserves_kwargs(self):
        """Test que kwargs arbitrarios se guardan en el entry."""
        try:
            log = self.setup()
            entry = log.append(
                "task_added",
                task_id="T-001",
                task_text="Revisar PRs",
                target="week",
                priority=1,
            )

            assert entry["task_id"] == "T-001"
            assert entry["task_text"] == "Revisar PRs"
            assert entry["target"] == "week"
            assert entry["priority"] == 1

            # Verificar persistencia
            loaded = log.read_day()
            assert loaded[0]["task_id"] == "T-001"

            print("✅ Test: kwargs arbitrarios se preservan en entry")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test entry_preserves_kwargs falló: {e}")
            self.failed += 1
        finally:
            self.teardown()

    def test_log_dir_creation(self):
        """Test que el directorio data/log se crea automáticamente."""
        try:
            log = self.setup()
            expected_dir = os.path.join(self.temp_dir, "data", "log")
            assert not os.path.exists(expected_dir), "Dir no debería existir aún"

            log.append("first_event")
            assert os.path.exists(expected_dir), "Dir debería crearse con append"

            print("✅ Test: directorio data/log se crea automáticamente")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test log_dir_creation falló: {e}")
            self.failed += 1
        finally:
            self.teardown()

    def run_all(self):
        """Ejecutar todos los tests."""
        print("\n🧪 TESTS: worklog/event_log.py")
        print("=" * 50)

        self.test_append_creates_file()
        self.test_append_multiple_entries()
        self.test_read_day_empty()
        self.test_read_day_today()
        self.test_read_range()
        self.test_corrupted_file_returns_empty()
        self.test_entry_preserves_kwargs()
        self.test_log_dir_creation()

        print(f"\n📊 Resultado: ✅ {self.passed} | ❌ {self.failed}")
        return self.failed == 0


if __name__ == "__main__":
    tester = TestEventLog()
    success = tester.run_all()
    sys.exit(0 if success else 1)
