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
from brackets.core.menu_navigator import MenuNavigator, MenuOption


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
        if read_single_key_fn is not None:
            self.read_single_key = read_single_key_fn
        elif input_fn is not None and input_fn is not input:
            self.read_single_key = lambda prompt="": self.input(prompt)
        else:
            self.read_single_key = None
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

    def prompt_topic_or_project_selection(self, week: Optional[WeekSchedule] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Permite vincular a un Topic (que hereda su proyecto) o directamente a un Proyecto.
        Devuelve (project_id, topic_id).
        """
        topics = []
        if week and week.topic_ids:
            for tid in week.topic_ids:
                top = self.manager.topics.get(tid)
                if top:
                    topics.append(top)
        if not topics:
            topics = list(self.manager.topics.values())

        projects = self.manager.list_projects()

        self.print("\n🎯 ASIGNACIÓN JERÁRQUICA (Proyecto / Topic):")
        opt_idx = 1
        topic_map = {}
        if topics:
            self.print("  Topics disponibles:")
            for top in topics:
                self.print(f"    [{opt_idx}] 🎯 {top.title} ([{top.project_id}])")
                topic_map[str(opt_idx)] = top
                opt_idx += 1

        proj_map = {}
        if projects:
            self.print("  Proyectos directos:")
            for p in projects:
                self.print(f"    [{opt_idx}] 📁 {p.id} ({p.name})")
                proj_map[str(opt_idx)] = p
                opt_idx += 1

        self.print("    [0] Ninguno / Sin vincular")
        self.print("    [+] Crear nuevo Topic o Proyecto")

        choice = self.input("Selecciona opción (0 por defecto): ").strip()
        if not choice or choice in ("0", "n", "no"):
            return None, None

        if choice == "+":
            sub_choice = self.input("¿Crear [t] Topic o [p] Proyecto?: ").strip().lower()
            if sub_choice.startswith("p"):
                new_pid = self.input("Código del nuevo proyecto (ej: AMR_LOGISTICS): ").strip()
                if new_pid:
                    new_pname = self.input(f"Nombre descriptivo para '{new_pid}': ").strip()
                    p_obj = self.manager.ensure_project(new_pid, name=new_pname)
                    return p_obj.id, None
            else:
                top_title = self.input("Título del nuevo Topic: ").strip()
                if top_title:
                    pid = self.prompt_project_selection() or "GENERAL"
                    topic = self.manager.create_topic(
                        title=top_title,
                        project_id=pid,
                        year=week.year if week else None,
                        week_num=week.week_number if week else None
                    )
                    return topic.project_id, topic.id
            return None, None

        if choice in topic_map:
            chosen_topic = topic_map[choice]
            return chosen_topic.project_id, chosen_topic.id
        elif choice in proj_map:
            chosen_proj = proj_map[choice]
            return chosen_proj.id, None

        for p in projects:
            if choice.upper() in (p.id.upper(), p.name.upper()):
                return p.id, None

        return None, None

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

        if week.topic_ids:
            self.print("🎯 TOPICS DE LA SEMANA:")
            for tid in week.topic_ids:
                top = self.manager.topics.get(tid)
                if top:
                    proj_tag = f" [{top.project_id}]" if top.project_id else ""
                    self.print(f"  • {top.title}{proj_tag}")
            self.print("-" * 65)

        self.print("📋 TAREAS DE HOY:")
        if today_tasks:
            for idx, task in enumerate(today_tasks, start=1):
                status_box = "[x]" if task.is_done else ("[ ] ~~" if task.is_cancelled else "[ ]")
                suffix = "~~" if task.is_cancelled else ""
                proj_tag = f" [{task.project_id}]" if task.project_id else ""
                self.print(f"  [{idx}] {status_box} {task.title}{proj_tag}{suffix}")
        else:
            self.print("  (No hay tareas asignadas para este día)")

        week_pending = [
            self.manager.tasks[tid] for tid in week.week_task_ids
            if tid in self.manager.tasks and self.manager.tasks[tid].is_pending and tid not in day.task_ids
        ]
        if week_pending:
            self.print("\n📋 TAREAS DE LA SEMANA (SIN DÍA FIJO):")
            for t in week_pending:
                proj_tag = f" [{t.project_id}]" if t.project_id else ""
                self.print(f"  ⏳ {t.title}{proj_tag}")

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

        now = datetime.now()
        is_weekend_missing = now.weekday() in (5, 6) and not any(d.day_number == now.day for d in week.days)
        if is_weekend_missing:
            day_name = "Sábado" if now.weekday() == 5 else "Domingo"
            self.print(f"\n⚡ Fin de semana detectado: pulsa [+] para activar {day_name} {now.day} (Intervención/Guardia)")

        self.print("\n" + "=" * 65)
        self.print("  [t] 📋 Tareas      [n] 📝 Notas      [p] 📁 Proyectos      [d] 📅 Día")
        self.print("-" * 65)
        self.print("  [0/b/Esc] Menú General                         [q] Salir")
        self.print("=" * 65)

        return ordered_task_ids

    def _sync_from_markdown_if_exists(self, week: WeekSchedule) -> None:
        """Sincroniza cambios hechos a mano en el .md de la semana activa hacia la BD YAML y regenera el Markdown limpio."""
        from brackets.utils.legacy_utils import generate_filename
        from brackets.managers.markdown_sync_service import MarkdownSyncService
        md_path = generate_filename(
            year=week.year,
            month=week.month,
            week=week.week_number,
            directory=self.vault_root
        )
        if os.path.exists(md_path):
            service = MarkdownSyncService(self.manager, self.vault_root)
            if service.sync_week_from_markdown(md_path, week.year, week.week_number):
                self._sync_markdown(week)

    def run(self) -> str:
        """Bucle principal de interacción del Hub Diario. Retorna 'menu' o 'exit'."""
        first_iteration = True
        while True:
            week, day = self._get_active_week_and_day()
            if not week or not day:
                self.print("\n⚠️ No se encontró una semana activa para mostrar el Hub Diario.")
                self.print("   Crea una bitácora semanal primero o revisa data/weeks/.")
                self.input("\nPresiona Enter para ir al menú principal...")
                return "menu"

            # Sincronización automática de cambios manuales en Markdown al abrir el hub
            if first_iteration:
                self._sync_from_markdown_if_exists(week)
                first_iteration = False

            # Arrastre automático día a día de tareas pendientes previas
            if self.manager.rollover_day_tasks(week, day.day_number) > 0:
                self._sync_markdown(week)

            ordered_task_ids = self.render_dashboard(week, day)

            if self.read_single_key:
                choice = self.read_single_key("Selecciona una opción: ").strip().lower()
            else:
                choice = self.input("Selecciona una opción: ").strip().lower()

            if choice in ("q", "exit"):
                self.clear_screen()
                self.print("\n👋 ¡Hasta luego!")
                return "exit"

            if choice in ("0", "b", "menu", "back", "volver", "__ESC__", "\x1b"):
                return "menu"

            if choice == "t":
                res = self.manage_tasks_menu(week, day, ordered_task_ids)
                if res == "menu":
                    return "menu"
                if res == "exit":
                    return "exit"
                continue

            if choice in ("n", "m"):
                from brackets.core.note_crud_controller import NoteCrudController
                crud = NoteCrudController(
                    entity_manager=self.manager,
                    current_week=week,
                    vault_root=self.vault_root,
                    input_fn=self.input,
                    print_fn=self.print,
                    clear_screen_fn=self.clear_screen,
                    read_single_key_fn=self.read_single_key
                )
                res = crud.run()
                if res == "menu":
                    return "menu"
                if res == "exit":
                    return "exit"
                continue

            if choice == "p":
                from brackets.core.project_backlog_controller import ProjectBacklogController
                ctrl = ProjectBacklogController(
                    entity_manager=self.manager,
                    current_week=week,
                    current_day=day,
                    vault_root=self.vault_root,
                    input_fn=self.input,
                    print_fn=self.print,
                    clear_screen_fn=self.clear_screen,
                    read_single_key_fn=self.read_single_key
                )
                res = ctrl.run()
                if res == "menu":
                    return "menu"
                if res == "exit":
                    return "exit"
                continue

            if choice in ("d", "s"):
                res = self.manage_day_menu(week)
                if res == "menu":
                    return "menu"
                if res == "exit":
                    return "exit"
                continue

            # Atajos directos para compatibilidad y rapidez
            if choice == "c":
                self._action_toggle_task(week, day, ordered_task_ids)
                continue

            if choice == "j":
                self._action_jira_task(week, day)
                continue

            if choice == "+":
                self._action_add_intervention_day(week)
                continue

            if choice == "a":
                self._action_schedule_topic(week, day)
                continue

    def manage_tasks_menu(self, week: WeekSchedule, day: DaySchedule, ordered_task_ids: List[str]) -> Optional[str]:
        """Subpantalla interactiva de gestión de tareas con MenuNavigator (Opción B)."""
        options = [
            MenuOption("1", "➕ Nueva Tarea HOY", "new_task", aliases=["n"]),
            MenuOption("2", "🎫 Tarea Jira HOY", "jira_task", aliases=["j"]),
            MenuOption("3", "✅ Marcar Tarea (completar / reactivar)", "toggle_task", aliases=["c", "m"]),
            MenuOption("4", "🗑️  Borrar Tarea", "delete_task", aliases=["d", "b"]),
            MenuOption("5", "🎯 Crear nuevo Topic Semanal", "new_topic", aliases=["t"]),
            MenuOption("6", "📋 Nueva Tarea SEMANAL (sin día fijo)", "new_week_task", aliases=["w"]),
            MenuOption("7", "➡️  Agendar Tarea Semanal / Topic a HOY", "schedule_topic", aliases=["a"]),
        ]

        title = f"📋 G E S T I Ó N  D E  T A R E A S  (Día {day.day_number})"
        navigator = MenuNavigator(
            title=title,
            options=options,
            show_back=True,
            show_main_menu=True,
            print_fn=self.print,
            input_fn=self.input,
            read_single_key_fn=self.read_single_key,
            clear_screen_fn=self.clear_screen,
        )

        while True:
            nav_status, opt = navigator.prompt()
            if nav_status == "back":
                return "back"
            if nav_status == "menu":
                return "menu"
            if nav_status == "exit":
                return "exit"

            if opt:
                if opt.action_id == "new_task":
                    self._action_new_task(week, day)
                    return "refresh"
                elif opt.action_id == "jira_task":
                    self._action_jira_task(week, day)
                    return "refresh"
                elif opt.action_id == "toggle_task":
                    self._action_toggle_task(week, day, ordered_task_ids)
                    return "refresh"
                elif opt.action_id == "delete_task":
                    self._action_delete_task(week, day, ordered_task_ids)
                    return "refresh"
                elif opt.action_id == "new_topic":
                    self._action_new_topic(week)
                    return "refresh"
                elif opt.action_id == "new_week_task":
                    self._action_new_week_task(week)
                    return "refresh"
                elif opt.action_id == "schedule_topic":
                    self._action_schedule_topic(week, day)
                    return "refresh"

    def manage_day_menu(self, week: WeekSchedule) -> Optional[str]:
        """Subpantalla interactiva de selección de día y guardias con MenuNavigator (Opción B)."""
        options = []
        for idx, d in enumerate(week.days, start=1):
            is_active = " 👈 (Activo)" if d.day_number == self.active_day_number else ""
            note = f" ({d.location_note})" if d.location_note else ""
            options.append(MenuOption(
                str(idx),
                f"{d.location_emoji} Día {d.day_number}{note}{is_active}",
                f"day_{d.day_number}",
                aliases=[str(d.day_number)]
            ))
        options.append(MenuOption(
            "+",
            "🛠️ Activar Guardia / Intervención Fin de Semana",
            "add_day",
            aliases=["intervencion", "guardia"]
        ))

        navigator = MenuNavigator(
            title=f"📅 S E L E C C I Ó N  D E  D Í A  (Semana W{week.week_number:02d} / {week.year})",
            options=options,
            show_back=True,
            show_main_menu=True,
            print_fn=self.print,
            input_fn=self.input,
            read_single_key_fn=self.read_single_key,
            clear_screen_fn=self.clear_screen,
        )

        nav_status, opt = navigator.prompt()
        if nav_status == "back":
            return "back"
        if nav_status == "menu":
            return "menu"
        if nav_status == "exit":
            return "exit"

        if opt:
            if opt.action_id == "add_day":
                self._action_add_intervention_day(week)
                return "refresh"
            elif opt.action_id.startswith("day_"):
                day_num = int(opt.action_id.replace("day_", ""))
                self.active_day_number = day_num
                return "refresh"
        return "refresh"

    def _action_new_task(self, week: WeekSchedule, day: DaySchedule) -> None:
        text = self.input("📝 Texto de la nueva tarea: ").strip()
        if text:
            proj_id, topic_id = self.prompt_topic_or_project_selection(week)
            self.manager.create_task(
                title=text,
                project_id=proj_id,
                topic_id=topic_id,
                year=week.year,
                week_num=week.week_number,
                day_number=day.day_number
            )
            self._sync_markdown(week)

    def _action_jira_task(self, week: WeekSchedule, day: DaySchedule) -> None:
        ticket_code = self.input("🎫 Código Jira (ej: ATLM-12703): ").strip()
        desc = self.input("📝 Descripción de la tarea: ").strip()
        if ticket_code and desc:
            proj_id, topic_id = self.prompt_topic_or_project_selection(week)
            jira_def = self.manager.ensure_jira_definition(ticket_code)
            full_title = f"{desc} {jira_def.id}"
            self.manager.create_task(
                title=full_title,
                project_id=proj_id,
                topic_id=topic_id,
                year=week.year,
                week_num=week.week_number,
                day_number=day.day_number
            )
            self._sync_markdown(week)

    def _action_new_week_task(self, week: WeekSchedule) -> None:
        text = self.input("📝 Texto de la tarea semanal (sin día fijo): ").strip()
        if text:
            proj_id, topic_id = self.prompt_topic_or_project_selection(week)
            self.manager.create_task(
                title=text,
                project_id=proj_id,
                topic_id=topic_id,
                is_week_task=True,
                year=week.year,
                week_num=week.week_number
            )
            self._sync_markdown(week)
            self.print("✅ Tarea añadida a las Tareas de la Semana.")
            self.input("Presiona Enter para continuar...")

    def _action_toggle_task(self, week: WeekSchedule, day: DaySchedule, ordered_task_ids: List[str]) -> None:
        if not ordered_task_ids:
            self.print("❌ No hay tareas para marcar.")
            self.input("Presiona Enter para continuar...")
            return
        num_str = self.input(f"Número de tarea (1-{len(ordered_task_ids)}): ").strip()
        try:
            num = int(num_str)
            if 1 <= num <= len(ordered_task_ids):
                target_id = ordered_task_ids[num - 1]
                self.manager.toggle_task(target_id)
                self._sync_markdown(week)
            else:
                self.print("❌ Número fuera de rango.")
                self.input("Presiona Enter para continuar...")
        except ValueError:
            self.print("❌ Ingresa un número válido.")
            self.input("Presiona Enter para continuar...")

    def _action_delete_task(self, week: WeekSchedule, day: DaySchedule, ordered_task_ids: List[str]) -> None:
        if not ordered_task_ids:
            self.print("❌ No hay tareas para borrar.")
            self.input("Presiona Enter para continuar...")
            return
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

    def _action_new_topic(self, week: WeekSchedule) -> None:
        text = self.input("📝 Texto del nuevo Topic semanal: ").strip()
        if text:
            proj_id = self.prompt_project_selection() or "GENERAL"
            topic = self.manager.create_topic(
                title=text,
                project_id=proj_id,
                year=week.year,
                week_num=week.week_number
            )
            task = self.manager.create_task(
                title=text,
                project_id=proj_id,
                topic_id=topic.id,
                is_week_task=True,
                year=week.year,
                week_num=week.week_number
            )
            self._sync_markdown(week)
            self.print(f"✅ Topic añadido a la semana: [{topic.project_id}] {topic.title}")
            self.input("Presiona Enter para continuar...")

    def _action_schedule_topic(self, week: WeekSchedule, day: DaySchedule) -> None:
        available_ids = list(week.week_task_ids) + list(week.topics_task_ids)
        seen = set()
        available_topics = []
        for tid in available_ids:
            if tid not in seen and tid in self.manager.tasks:
                seen.add(tid)
                t = self.manager.tasks[tid]
                if t.is_pending and tid not in day.task_ids:
                    available_topics.append(t)

        if not available_topics:
            self.print("\n⚠️ No hay topics pendientes disponibles para agendar a hoy.")
            self.input("Presiona Enter para continuar...")
            return

        self.print(f"\n📋 TOPICS SEMANALES DISPONIBLES PARA AGENDAR AL DÍA {day.day_number}:")
        for idx, t in enumerate(available_topics, start=1):
            top_tag = f" 🎯[{self.manager.topics[t.topic_id].title}]" if (t.topic_id and t.topic_id in self.manager.topics) else ""
            proj_tag = f" [{t.project_id}]" if t.project_id else ""
            self.print(f"  [{idx}] {t.title}{top_tag}{proj_tag}")

        t_choice = self.input(f"Selecciona topic a agendar a HOY (1-{len(available_topics)}, 0 para cancelar): ").strip()
        try:
            t_idx = int(t_choice)
            if 1 <= t_idx <= len(available_topics):
                chosen_topic = available_topics[t_idx - 1]
                self.manager.assign_topic_to_day(week, chosen_topic.id, day.day_number)
                self._sync_markdown(week)
                self.print(f"✅ Topic '{chosen_topic.title}' agendado para HOY (Día {day.day_number}).")
                self.input("Presiona Enter para continuar...")
        except ValueError:
            pass

    def _action_add_intervention_day(self, week: WeekSchedule) -> None:
        now = datetime.now()
        def_day = now.day if now.weekday() in (5, 6) else (week.days[-1].day_number + 1)
        num_input = self.input(f"Número de día a añadir ({def_day} por defecto): ").strip()
        try:
            add_num = int(num_input) if num_input else def_day
        except ValueError:
            add_num = def_day

        self.print("\nSelecciona ubicación/tipo:")
        self.print("  [1] 🛠️ Guardia / Intervención")
        self.print("  [2] 🏠 Teletrabajo")
        self.print("  [3] 🚗 Oficina / Presencial")
        loc_opt = self.input("Opción (1 por defecto): ").strip()
        if loc_opt == "2":
            emoji, note = "🏠", "Teletrabajo"
        elif loc_opt == "3":
            emoji, note = "🚗", "Oficina"
        else:
            emoji, note = "🛠️", "Intervención"

        new_day = self.manager.add_day_to_week(
            week=week,
            day_number=add_num,
            location_emoji=emoji,
            location_note=note
        )
        self.active_day_number = new_day.day_number
        self._sync_markdown(week)
        self.print(f"✅ ¡Día {add_num} ({emoji} {note}) añadido con éxito a la semana!")
        self.input("Presiona Enter para continuar...")
