#!/usr/bin/env python3
"""
Tests unitarios para el motor de Tareas y Reuniones Recurrentes (RecurringTask).
"""

import os
import shutil
import tempfile
import unittest

from brackets.models.entities import RecurringTask, WeekSchedule, DaySchedule
from brackets.managers.entity_manager import EntityManager


class TestRecurringTasks(unittest.TestCase):
    """Pruebas para definición, persistencia, idempotencia y aplicación de recurrentes."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.mock_source = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "mock"
        )
        shutil.copytree(self.mock_source, os.path.join(self.tmp_dir, "mock_data"))
        self.data_dir = os.path.join(self.tmp_dir, "mock_data")
        self.manager = EntityManager(self.data_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_recurring_model_and_persistence(self):
        """Valida que una tarea recurrente se cree, persista y recargue con todos sus atributos."""
        rec = self.manager.create_recurring_task(
            title="Daily S^3",
            recurrence_type="weekly_days",
            days_of_week=[0, 2, 4],
            project_id="DAILY_PROJECT"
        )
        self.assertTrue(rec.id.startswith("REC-"))
        self.assertEqual(rec.title, "Daily S^3")
        self.assertEqual(rec.days_of_week, [0, 2, 4])
        self.assertTrue(rec.active)

        # Recargar desde disco
        new_manager = EntityManager(self.data_dir)
        self.assertIn(rec.id, new_manager.recurring_tasks)
        loaded = new_manager.recurring_tasks[rec.id]
        self.assertEqual(loaded.title, "Daily S^3")
        self.assertEqual(loaded.days_of_week, [0, 2, 4])
        self.assertEqual(loaded.project_id, "DAILY_PROJECT")

    def test_apply_weekly_days_recurring(self):
        """Verifica la inyección de reuniones de días fijos (Lunes, Miércoles, Viernes)."""
        rec = self.manager.create_recurring_task(
            title="Daily S^3",
            recurrence_type="weekly_days",
            days_of_week=[0, 2, 4]  # L, X, V
        )

        week = self.manager.load_week(2026, 34)
        self.assertIsNotNone(week)

        injected = self.manager.apply_recurring_tasks(week)
        self.assertEqual(injected, 3)

        # Verificar que las tareas se hayan creado en los días correspondientes
        # Día 0 (Lunes), Día 2 (Miércoles), Día 4 (Viernes)
        monday = week.days[0]
        wednesday = week.days[2]
        friday = week.days[4]

        # Cada uno debe contener una tarea con el título y recurring_id
        mon_tasks = [self.manager.tasks[tid] for tid in monday.task_ids if tid in self.manager.tasks]
        self.assertTrue(any(t.title == "Daily S^3" and t.recurring_id == rec.id for t in mon_tasks))

        wed_tasks = [self.manager.tasks[tid] for tid in wednesday.task_ids if tid in self.manager.tasks]
        self.assertTrue(any(t.title == "Daily S^3" and t.recurring_id == rec.id for t in wed_tasks))

        fri_tasks = [self.manager.tasks[tid] for tid in friday.task_ids if tid in self.manager.tasks]
        self.assertTrue(any(t.title == "Daily S^3" and t.recurring_id == rec.id for t in fri_tasks))

    def test_apply_interval_weeks_recurring(self):
        """Valida que una tarea de cada 4 semanas solo se inyecte en las semanas que correspondan."""
        rec = self.manager.create_recurring_task(
            title="Renovar Accesos",
            recurrence_type="interval_weeks",
            interval_weeks=4,
            base_week=34,
            day_of_week=4  # Viernes
        )

        week34 = self.manager.load_week(2026, 34)
        injected34 = self.manager.apply_recurring_tasks(week34)
        self.assertEqual(injected34, 1)
        fri_tasks = [self.manager.tasks[tid] for tid in week34.days[4].task_ids if tid in self.manager.tasks]
        self.assertTrue(any(t.title == "Renovar Accesos" and t.recurring_id == rec.id for t in fri_tasks))

        # Crear semana 35 (no le toca por ser 35 - 34 = 1, no múltiplo de 4)
        week35 = WeekSchedule(
            year=2026,
            month=8,
            week_number=35,
            days=[DaySchedule(day_number=24 + i) for i in range(5)]
        )
        self.manager.save_week(week35)

        injected35 = self.manager.apply_recurring_tasks(week35)
        self.assertEqual(injected35, 0)

        # Crear semana 38 (le toca: 38 - 34 = 4, múltiplo de 4)
        week38 = WeekSchedule(
            year=2026,
            month=9,
            week_number=38,
            days=[DaySchedule(day_number=14 + i) for i in range(5)]
        )
        self.manager.save_week(week38)

        injected38 = self.manager.apply_recurring_tasks(week38)
        self.assertEqual(injected38, 1)

    def test_apply_recurring_tasks_idempotence(self):
        """Verifica que ejecutar la inyección múltiples veces NO duplica tareas."""
        self.manager.create_recurring_task(
            title="Daily S^3",
            recurrence_type="weekly_days",
            days_of_week=[0, 2, 4]
        )
        week = self.manager.load_week(2026, 34)
        first_run = self.manager.apply_recurring_tasks(week)
        self.assertEqual(first_run, 3)

        # Segunda ejecución inmediata
        second_run = self.manager.apply_recurring_tasks(week)
        self.assertEqual(second_run, 0)

        # Conteo de tareas en Lunes
        monday = week.days[0]
        daily_count = sum(
            1 for tid in monday.task_ids
            if tid in self.manager.tasks and self.manager.tasks[tid].title == "Daily S^3"
        )
        self.assertEqual(daily_count, 1)

    def test_toggle_and_delete_recurring(self):
        """Verifica pausar, reactivar y borrar tareas recurrentes."""
        rec = self.manager.create_recurring_task(
            title="Reunión 1:1 Semanal",
            recurrence_type="weekly_days",
            days_of_week=[1]
        )
        self.assertTrue(rec.active)

        # Pausar
        toggled = self.manager.toggle_recurring_task(rec.id)
        self.assertFalse(toggled.active)

        # No debe inyectarse al estar pausada
        week = self.manager.load_week(2026, 34)
        injected = self.manager.apply_recurring_tasks(week)
        self.assertEqual(injected, 0)

        # Eliminar
        deleted = self.manager.delete_recurring_task(rec.id)
        self.assertTrue(deleted)
        self.assertNotIn(rec.id, self.manager.recurring_tasks)


if __name__ == "__main__":
    unittest.main()
