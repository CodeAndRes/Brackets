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

        self.active_day_number: Optional[int] = None

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

        if not week or not week.days:
            return None, None

        # Si el usuario ha fijado un día activo, buscarlo
        if self.active_day_number is not None:
            for day in week.days:
                if day.day_number == self.active_day_number:
                    return week, day

        # Buscar el día de hoy dentro de la semana
        for day in week.days:
            if day.day_number == today_day:
                self.active_day_number = day.day_number
                return week, day

        # Si hoy no está en los días de la semana (ej: fin de semana), usar el último día disponible
        active_day = week.days[-1]
        self.active_day_number = active_day.day_number
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

    def prompt_project_selection(self) -> Optional[str]:
        """Muestra la lista de proyectos para asociar a una tarea, nota o referencia."""
        projects = self.manager.list_projects()
        self.print("\n📁 VINCULAR A PROYECTO:")
        if projects:
            for idx, p in enumerate(projects, start=1):
                self.print(f"  [{idx}] {p.id} ({p.name})")
        else:
            self.print("  (No hay proyectos registrados)")
        self.print("  [0] Ninguno / Sin vincular")
        self.print("  [+] Crear y vincular nuevo proyecto")

        p_choice = self.input("Selecciona proyecto (0 por defecto): ").strip()
        if not p_choice or p_choice in ("0", "n", "no"):
            return None

        if p_choice == "+":
            new_pid = self.input("Código del nuevo proyecto (ej: AMR_LOGISTICS): ").strip()
            if new_pid:
                new_pname = self.input(f"Nombre descriptivo para '{new_pid}': ").strip()
                p_obj = self.manager.ensure_project(new_pid, name=new_pname)
                return p_obj.id
            return None

        try:
            p_idx = int(p_choice)
            if 1 <= p_idx <= len(projects):
                return projects[p_idx - 1].id
        except ValueError:
            # Si el usuario escribe directamente el nombre/código
            for p in projects:
                if p_choice.upper() in (p.id.upper(), p.name.upper()):
                    return p.id

        return None

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
                proj_tag = f" [{task.project_id}]" if task.project_id else ""
                self.print(f"  [{idx}] {status_box} {task.title}{proj_tag}{suffix}")
        else:
            self.print("  (No hay tareas asignadas para este día)")

        self.print("\n📝 NOTAS DE LA SEMANA:")
        rendered_notes = 0
        for nid in week.note_ids:
            note = self.manager.notes.get(nid)
            if note:
                if note.title:
                    proj_tag = f" [{note.project_id}]" if note.project_id else ""
                    self.print(f"  📌 {note.title}{proj_tag}")
                    for line in note.content[:2]:
                        self.print(f"     • {line[:60]}{'...' if len(line)>60 else ''}")
                else:
                    for line in note.content[:3]:
                        self.print(f"  • {line[:60]}{'...' if len(line)>60 else ''}")
                rendered_notes += 1
        if rendered_notes == 0:
            self.print("  (Sin notas registradas)")

        self.print("\n" + "-" * 65)
        self.print("[c] Marcar/Desmarcar Tarea   [n] Nueva Tarea Día      [j] Tarea Jira")
        self.print("[d] Borrar Tarea             [m] Añadir Nota Semana   [s] Cambiar Día Activo")
        self.print("[b] Menú General             [q] Salir")
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

            if choice == "s":
                # Cambiar día activo
                self.print("\n📅 DÍAS DE LA SEMANA:")
                for idx, d in enumerate(week.days, start=1):
                    current_marker = " 👈 (Activo)" if d.day_number == day.day_number else ""
                    note_str = f" ({d.location_note})" if d.location_note else ""
                    task_count = len(d.task_ids)
                    self.print(f"  [{idx}] {d.location_emoji} Día {d.day_number}{note_str} - {task_count} tarea(s){current_marker}")

                day_choice_str = self.input(f"\nSelecciona día (1-{len(week.days)}): ").strip()
                try:
                    d_idx = int(day_choice_str)
                    if 1 <= d_idx <= len(week.days):
                        self.active_day_number = week.days[d_idx - 1].day_number
                    else:
                        self.print("❌ Selección fuera de rango.")
                        self.input("Presiona Enter para continuar...")
                except ValueError:
                    self.print("❌ Ingresa un número válido.")
                    self.input("Presiona Enter para continuar...")

            elif choice == "c":
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
                    proj_id = self.prompt_project_selection()
                    self.manager.create_task(
                        title=text,
                        project_id=proj_id,
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
                    proj_id = self.prompt_project_selection()
                    jira_def = self.manager.ensure_jira_definition(ticket_code)
                    full_title = f"{desc} {jira_def.id}"
                    self.manager.create_task(
                        title=full_title,
                        project_id=proj_id,
                        year=week.year,
                        week_num=week.week_number,
                        day_number=day.day_number
                    )
                    self._sync_markdown(week)

            elif choice == "m":
                # Añadir nota semanal estructurada (Título + Viñetas + Proyecto)
                title = self.input("📌 Título de la nota: ").strip()
                self.print("📝 Introduce las viñetas/contenido de la nota (línea vacía para terminar):")
                content_lines: List[str] = []
                while True:
                    line = self.input("  • ").strip()
                    if not line:
                        break
                    content_lines.append(line)

                if title or content_lines:
                    proj_id = self.prompt_project_selection()
                    self.manager.add_note(
                        title=title if title else None,
                        content=content_lines,
                        project_id=proj_id,
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
