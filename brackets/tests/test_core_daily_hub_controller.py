#!/usr/bin/env python3
"""
Tests para DailyHubController en brackets/core/daily_hub_controller.py
"""

import sys
import os
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from brackets.models.entities import WeekSchedule, DaySchedule
from brackets.managers.entity_manager import EntityManager
from brackets.core.daily_hub_controller import DailyHubController


class TestCoreDailyHubController(unittest.TestCase):
    """Pruebas unitarias para el controlador del Hub Diario interactivo."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.mock_source = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "mock"
        )
        self.mock_data_dir = os.path.join(self.tmp_dir, "data")
        shutil.copytree(self.mock_source, self.mock_data_dir)

        self.entity_manager = EntityManager(self.mock_data_dir)
        self.output_lines = []

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _mock_print(self, *args, **kwargs):
        line = " ".join(str(a) for a in args)
        self.output_lines.append(line)

    def test_render_dashboard(self):
        """Verifica que el dashboard imprima la cabecera, tareas de hoy y comandos."""
        controller = DailyHubController(
            vault_root=self.tmp_dir,
            entity_manager=self.entity_manager,
            print_fn=self._mock_print
        )

        week = self.entity_manager.load_week(2026, 34)
        day = week.days[0]  # Día 17

        ordered_ids = controller.render_dashboard(week, day)
        output_text = "\n".join(self.output_lines)

        self.assertEqual(len(ordered_ids), 2)
        self.assertIn("🗓️ BITÁCORA:", output_text)
        self.assertIn("🚗 Día 17 (Oficina)", output_text)
        self.assertIn("Pruebas de AMRs para la vuelta", output_text)
        self.assertIn("[c] Marcar/Desmarcar", output_text)

    def test_run_toggle_task(self):
        """Simula pulsar 'c', seleccionar tarea '1' y luego 'q' para salir."""
        inputs = ["c", "1", "q"]

        def mock_input(prompt=""):
            return inputs.pop(0)

        controller = DailyHubController(
            vault_root=self.tmp_dir,
            entity_manager=self.entity_manager,
            input_fn=mock_input,
            print_fn=self._mock_print
        )
        controller.active_day_number = 17

        result = controller.run()
        self.assertEqual(result, "exit")

        # Verificar que la tarea TSK-0010 cambió de estado
        task = self.entity_manager.tasks.get("TSK-0010")
        self.assertFalse(task.is_done)  # Antes estaba done, ahora es pending

    def test_run_switch_day(self):
        """Simula pulsar 's', elegir día 4 (día 20) y luego 'q'."""
        inputs = ["s", "4", "q"]

        def mock_input(prompt=""):
            return inputs.pop(0)

        controller = DailyHubController(
            vault_root=self.tmp_dir,
            entity_manager=self.entity_manager,
            input_fn=mock_input,
            print_fn=self._mock_print
        )

        result = controller.run()
        self.assertEqual(result, "exit")
        self.assertEqual(controller.active_day_number, 20)

    def test_run_add_new_task(self):
        """Simula pulsar 'n', escribir tarea, elegir proyecto 0 (sin vincular) y luego 'q' para salir."""
        inputs = ["n", "Configurar nuevo endpoint en backend", "0", "q"]

        def mock_input(prompt=""):
            return inputs.pop(0)

        controller = DailyHubController(
            vault_root=self.tmp_dir,
            entity_manager=self.entity_manager,
            input_fn=mock_input,
            print_fn=self._mock_print
        )

        result = controller.run()
        self.assertEqual(result, "exit")

        # Verificar que se creó una tarea con ese título
        created = [t for t in self.entity_manager.tasks.values() if "Configurar nuevo endpoint" in t.title]
        self.assertEqual(len(created), 1)

    def test_run_add_jira_task(self):
        """Simula pulsar 'j', introducir código Jira, descripción, proyecto 0 y luego 'q'."""
        inputs = ["j", "ATLM-88888", "Ajustar timeout de conexión", "0", "q"]

        def mock_input(prompt=""):
            return inputs.pop(0)

        controller = DailyHubController(
            vault_root=self.tmp_dir,
            entity_manager=self.entity_manager,
            input_fn=mock_input,
            print_fn=self._mock_print
        )

        result = controller.run()
        self.assertEqual(result, "exit")

        # Verificar definición y tarea
        jira_def = self.entity_manager.definitions.get("[🎫ATLM-88888]")
        self.assertIsNotNone(jira_def)
        created = [t for t in self.entity_manager.tasks.values() if "[🎫ATLM-88888]" in t.title]
        self.assertEqual(len(created), 1)

    def test_run_add_note(self):
        """Simula pulsar 'm', introducir título, viñeta, fin de viñetas, proyecto 0 y luego 'q'."""
        inputs = [
            "m",
            "Revisión de Arquitectura",
            "Revisión con equipo completada sin bloqueos",
            "",
            "0",
            "q"
        ]

        def mock_input(prompt=""):
            return inputs.pop(0)

        controller = DailyHubController(
            vault_root=self.tmp_dir,
            entity_manager=self.entity_manager,
            input_fn=mock_input,
            print_fn=self._mock_print
        )

        result = controller.run()
        self.assertEqual(result, "exit")

        created = [n for n in self.entity_manager.notes.values() if n.title == "Revisión de Arquitectura"]
        self.assertEqual(len(created), 1)
        self.assertEqual(created[0].content, ["Revisión con equipo completada sin bloqueos"])

    def test_run_navigate_to_main_menu(self):
        """Simula pulsar 'b' para ir al menú principal."""
        inputs = ["b"]

        def mock_input(prompt=""):
            return inputs.pop(0)

        controller = DailyHubController(
            vault_root=self.tmp_dir,
            entity_manager=self.entity_manager,
            input_fn=mock_input,
            print_fn=self._mock_print
        )

        result = controller.run()
        self.assertEqual(result, "menu")


if __name__ == "__main__":
    unittest.main()
