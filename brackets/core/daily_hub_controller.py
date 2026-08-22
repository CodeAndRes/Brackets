#!/usr/bin/env python3
"""
Controlador del Hub Diario Interactivo (CLI Dashboard) para Brackets.
"""

from __future__ import annotations
import os
import sys
from datetime import datetime
from typing import Callable, Optional, List, Tuple

from brackets.models.entities import WeekSchedule, DaySchedule, Task, Note
from brackets.managers.entity_manager import EntityManager
from brackets.generators.bitacora_renderer import BitacoraRenderer
from brackets.utils.legacy_utils import generate_filename


class DailyHubController:
    """Gestiona la pantalla interactiva del día actual y las acciones rápidas por teclado."""

    def __init__(
        self,
        vault_root: str,
        entity_manager: Optional[EntityManager] = None,
        input_fn: Callable[[str], str] = input,
        print_fn: Callable[..., None] = print,
        read_single_key_fn: Optional[Callable[[str], str]] = None,
        clear_screen_fn: Optional[Callable[[], None]] = None
    ):
        self.vault_root = os.path.abspath(vault_root)
        self.data_dir = os.path.join(self.vault_root, "data")
        self.notes_root = self.vault_root
        self.input = input_fn
        self.print = print_fn
        self.read_single_key = read_single_key_fn
        self.clear_screen = clear_screen_fn or (lambda: None)

        if entity_manager:
            self.manager = entity_manager
        else:
            # Si no existen las tablas en data/, usar mock o inicializar
            tables_dir = os.path.join(self.data_dir, "tables")
            if not os.path.exists(tables_dir):
                # Fallback al directorio mock si existe para demos
                mock_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "mock")
                if os.path.exists(mock_dir):
                    self.manager = EntityManager(mock_dir)
                else:
                    self.manager = EntityManager(self.data_dir)
            else:
                self.manager = EntityManager(self.data_dir)

    def _get_active_week_and_day(self) -> Tuple[Optional[WeekSchedule], Optional[DaySchedule]]:
        """Determina la semana y el día activo para la jornada actual."""
        now = datetime.now()
        iso_year, iso_week, _ = now.isocalendar()
        today_day = now.day

        # Intentar cargar la semana actual
        week = self.manager.load_week(iso_year, iso_week)
        if not week:
            # Si no hay semana actual cargada, buscar la última semana disponible en el manager
            if self.manager.weeks:
                last_key = sorted(self.manager.weeks.keys())[-1]
                week = self.manager.weeks[last_key]
            else:
                return None, None

        if not week:
            return None, None

        # Buscar el día de hoy dentro de la semana
        active_day = None
        for day in week.days:
            if day.day_number == today_day:
                active_day = day
                break

        # Si hoy no está en los días (ej: fin de semana o mock), tomar el primer día con tareas o el último disponible
        if not active_day and week.days:
            # Preferir un día que tenga tareas
            days_with_tasks = [d for d in week.days if d.task_ids]
            active_day = days_with_tasks[0] if days_with_tasks else week.days[0]

        return week, active_day

    def _get_target_md_filepath(self, week: WeekSchedule) -> str:
        """Calcula la ruta del archivo Markdown correspondiente a la semana."""
        return generate_filename(
            year=week.year,
            month=week.month,
            week=week.week_number,
            directory=self.notes_root
        )

    def _sync_markdown(self, week: WeekSchedule) -> None:
        """Regenera y guarda el archivo Markdown de la semana."""
        md_path = self._get_target_md_filepath(week)
        BitacoraRenderer.render_and_save_week(week, self.manager, md_path)

    def render_dashboard(self, week: WeekSchedule, day: DaySchedule) -> List[str]:
        """Imprime la pantalla del Hub Diario y devuelve los IDs de tareas mostradas en orden."""
        self.clear_screen()
        today_tasks: List[Task] = []
        ordered_task_ids: List[str] = []

        for tid in day.task_ids:
            task = self.manager.tasks.get(tid)
            if task:
                today_tasks.append(task)
                ordered_task_ids.append(tid)

        md_filename = os.path.basename(self._get_target_md_filepath(week))
        day_label = f"{day.location_emoji} Día {day.day_number}"
        if day.location_note:
            day_label += f" ({day.location_note})"

        self.print("=" * 65)
        self.print(f"🗓️ BITÁCORA: {md_filename} | HOY: {day_label}")
        self.print("=" * 65)

        self.print("📋 TAREAS DE HOY:")
        if today_tasks:
            for idx, task in enumerate(today_tasks, start=1):
                status_box = "[x]" if task.is_done else ("[ ] ~~" if task.is_cancelled else "[ ]")
                suffix = "~~" if task.is_cancelled else ""
                self.print(f"  [{idx}] {status_box} {task.title}{suffix}")
        else:
            self.print("  (No hay tareas asignadas para este día)")

        self.print("\n📝 NOTAS DE LA SEMANA:")
        rendered_notes = 0
        for nid in week.note_ids:
            note = self.manager.notes.get(nid)
            if note:
                for line in note.content[:3]:  # Mostrar hasta 3 viñetas destacadas
                    self.print(f"  • {line[:60]}{'...' if len(line)>60 else ''}")
                    rendered_notes += 1
        if rendered_notes == 0:
            self.print("  (Sin notas registradas)")

        self.print("\n" + "-" * 65)
        self.print("[c] Marcar/Desmarcar Tarea   [n] Nueva Tarea Hoy      [j] Tarea Jira")
        self.print("[d] Borrar Tarea             [m] Añadir Nota Semana   [b] Menú General")
        self.print("[q] Salir")
        self.print("=" * 65)

        return ordered_task_ids

    def run(self) -> str:
        """Bucle principal de interacción del Hub Diario. Retorna 'menu' o 'exit'."""
        while True:
            week, day = self._get_active_week_and_day()
            if not week or not day:
                self.print("\n⚠️ No se encontró una semana activa para mostrar el Hub Diario.")
                self.print("   Crea una bitácora semanal primero o revisa data/weeks/.")
                self.input("\nPresiona Enter para ir al menú principal...")
                return "menu"

            ordered_task_ids = self.render_dashboard(week, day)

            if self.read_single_key:
                choice = self.read_single_key("Selecciona una opción: ").strip().lower()
            else:
                choice = self.input("Selecciona una opción: ").strip().lower()

            if choice in ("q", "0", "exit"):
                self.clear_screen()
                self.print("\n👋 ¡Hasta luego!")
                return "exit"

            if choice in ("b", "menu"):
                return "menu"

            if choice == "c":
                # Marcar / desmarcar tarea
                if not ordered_task_ids:
                    self.print("❌ No hay tareas para marcar.")
                    self.input("Presiona Enter para continuar...")
                    continue

                num_str = self.input(f"Número de tarea (1-{len(ordered_task_ids)}): ").strip()
                try:
                    num = int(num_str)
                    if 1 <= num <= len(ordered_task_ids):
                        target_id = ordered_task_ids[num - 1]
                        toggled = self.manager.toggle_task(target_id)
                        self._sync_markdown(week)
                    else:
                        self.print("❌ Número fuera de rango.")
                        self.input("Presiona Enter para continuar...")
                except ValueError:
                    self.print("❌ Ingresa un número válido.")
                    self.input("Presiona Enter para continuar...")

            elif choice == "n":
                # Nueva tarea
                text = self.input("📝 Texto de la nueva tarea: ").strip()
                if text:
                    self.manager.create_task(
                        title=text,
                        year=week.year,
                        week_num=week.week_number,
                        day_number=day.day_number
                    )
                    self._sync_markdown(week)

            elif choice == "j":
                # Tarea con Jira Ticket
                ticket_code = self.input("🎫 Código Jira (ej: ATLM-12703): ").strip()
                desc = self.input("📝 Descripción de la tarea: ").strip()
                if ticket_code and desc:
                    jira_def = self.manager.ensure_jira_definition(ticket_code)
                    full_title = f"{desc} {jira_def.id}"
                    self.manager.create_task(
                        title=full_title,
                        definition_ids=[jira_def.id],
                        year=week.year,
                        week_num=week.week_number,
                        day_number=day.day_number
                    )
                    self._sync_markdown(week)

            elif choice == "m":
                # Añadir nota semanal
                note_text = self.input("📌 Nueva nota para la semana: ").strip()
                if note_text:
                    self.manager.add_note(
                        content=note_text,
                        year=week.year,
                        week_num=week.week_number
                    )
                    self._sync_markdown(week)

            elif choice == "d":
                # Borrar tarea
                if not ordered_task_ids:
                    self.print("❌ No hay tareas para borrar.")
                    self.input("Presiona Enter para continuar...")
                    continue

                num_str = self.input(f"Número de tarea a eliminar (1-{len(ordered_task_ids)}): ").strip()
                try:
                    num = int(num_str)
                    if 1 <= num <= len(ordered_task_ids):
                        target_id = ordered_task_ids[num - 1]
                        self.manager.delete_task(
                            task_id=target_id,
                            year=week.year,
                            week_num=week.week_number,
                            day_number=day.day_number
                        )
                        self._sync_markdown(week)
                    else:
                        self.print("❌ Número fuera de rango.")
                        self.input("Presiona Enter para continuar...")
                except ValueError:
                    self.print("❌ Ingresa un número válido.")
                    self.input("Presiona Enter para continuar...")
