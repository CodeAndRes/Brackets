#!/usr/bin/env python3
"""
Tests para el motor relacional YAML-First y el BitacoraRenderer de Brackets.
"""

import sys
import os
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from brackets.models.entities import Task, Note, Definition, WeekSchedule
from brackets.managers.entity_manager import EntityManager
from brackets.generators.bitacora_renderer import BitacoraRenderer


class TestRelationalBitacoraRenderer(unittest.TestCase):
    """Pruebas unitarias para EntityManager y BitacoraRenderer."""

    def setUp(self):
        # Crear directorio temporal y copiar mock data
        self.tmp_dir = tempfile.mkdtemp()
        self.mock_source = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "mock"
        )
        # Copiar estructura mock a temporal
        shutil.copytree(self.mock_source, os.path.join(self.tmp_dir, "mock_data"))
        self.data_dir = os.path.join(self.tmp_dir, "mock_data")
        self.manager = EntityManager(self.data_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_load_entities(self):
        """Verifica que las tablas de entidades se carguen correctamente."""
        self.assertGreater(len(self.manager.tasks), 0)
        self.assertGreater(len(self.manager.definitions), 0)
        self.assertGreater(len(self.manager.notes), 0)

        first_task = list(self.manager.tasks.values())[0]
        self.assertIsNotNone(first_task)
        self.assertTrue(first_task.id.startswith("TSK-"))

    def test_render_week_markdown(self):
        """Verifica que el renderizado Markdown coincida con el formato oficial de Bitácoras."""
        week = self.manager.load_week(2026, 34)
        self.assertIsNotNone(week)

        markdown = BitacoraRenderer.render_week(week, self.manager)

        # 1. Encabezado
        self.assertIn("# 🗓️Week 34", markdown)

        # 2. Topics
        self.assertIn("## ✅Topics", markdown)

        # 3. Notes
        self.assertIn("## 📝Notes", markdown)

        # 4. Días
        self.assertTrue(len(week.days) > 0)
        first_day = week.days[0]
        self.assertIn(f"## {first_day.location_emoji}{first_day.day_number}", markdown)

        # 5. Definiciones al pie
        self.assertIn("<!-- Definiciones -->", markdown)

    def test_toggle_task_and_regenerate(self):
        """Valida que alternar el estado de una tarea actualice el YAML y regenere el [x] en Markdown."""
        week = self.manager.load_week(2026, 34)
        
        # Buscar la primera tarea pendiente de la semana
        task_id = None
        for tid in week.topics_task_ids:
            t = self.manager.tasks.get(tid)
            if t and t.is_pending:
                task_id = tid
                break

        if not task_id:
            for d in week.days:
                for tid in d.task_ids:
                    t = self.manager.tasks.get(tid)
                    if t and t.is_pending:
                        task_id = tid
                        break
                if task_id:
                    break

        if not task_id:
            # Crear una tarea para el test si todas estaban completadas
            t_obj = self.manager.create_task(title="Tarea de prueba para toggle", year=2026, week_num=34, is_topic=True)
            task_id = t_obj.id

        task = self.manager.tasks.get(task_id)
        self.assertTrue(task.is_pending)

        # Cambiar a completada
        self.manager.toggle_task(task_id)
        self.assertTrue(task.is_done)
        self.assertIsNotNone(task.completed_at)

        # Regenerar markdown
        markdown = BitacoraRenderer.render_week(week, self.manager)
        self.assertIn(f"- [x] {task.title}", markdown)

        # Cambiar de nuevo a pendiente
        self.manager.toggle_task(task_id)
        self.assertTrue(task.is_pending)
        markdown2 = BitacoraRenderer.render_week(week, self.manager)
        self.assertIn(f"- [ ] {task.title}", markdown2)

    def test_add_jira_task_auto_definitions(self):
        """Valida que al añadir una tarea con Jira ticket, la definición aparezca automáticamente."""
        week = self.manager.load_week(2026, 34)

        # 1. Asegurar definición Jira
        jira_def = self.manager.ensure_jira_definition("ATLM-99999")
        self.assertEqual(jira_def.id, "[🎫ATLM-99999]")

        # 2. Crear tarea asociada al día 21
        new_task = self.manager.create_task(
            title=f"Revisar nueva funcionalidad de pagos {jira_def.id}",
            year=2026,
            week_num=34,
            day_number=21,
            definition_ids=[jira_def.id]
        )

        # 3. Renderizar markdown
        markdown = BitacoraRenderer.render_week(week, self.manager)

        self.assertIn(f"- [ ] Revisar nueva funcionalidad de pagos {jira_def.id}", markdown)
        self.assertIn("[🎫ATLM-99999]: https://mangospain.atlassian.net/browse/ATLM-99999", markdown)

    def test_add_note_and_render(self):
        """Valida que añadir una nota la incorpore en la sección ## 📝Notes."""
        week = self.manager.load_week(2026, 34)

        self.manager.add_note(
            content="Conclusión importante: El flujo de AMRs no requiere DXC.",
            year=2026,
            week_num=34
        )

        markdown = BitacoraRenderer.render_week(week, self.manager)
        self.assertIn("- Conclusión importante: El flujo de AMRs no requiere DXC.", markdown)


if __name__ == "__main__":
    unittest.main()
