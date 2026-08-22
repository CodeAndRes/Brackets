#!/usr/bin/env python3
"""
Gestor de Entidades y Almacén de Datos Relacional para Brackets.
"""

from __future__ import annotations
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import yaml

from brackets.models.entities import Task, Note, Definition, WeekSchedule, DaySchedule


class EntityManager:
    """Gestiona la persistencia y operaciones relacionales entre tablas de entidades y semanas."""

    def __init__(self, base_data_dir: str):
        self.base_data_dir = os.path.abspath(base_data_dir)
        self.tables_dir = os.path.join(self.base_data_dir, "tables")
        self.weeks_dir = os.path.join(self.base_data_dir, "weeks")

        os.makedirs(self.tables_dir, exist_ok=True)
        os.makedirs(self.weeks_dir, exist_ok=True)

        self.tasks: Dict[str, Task] = {}
        self.notes: Dict[str, Note] = {}
        self.definitions: Dict[str, Definition] = {}
        self.weeks: Dict[str, WeekSchedule] = {}  # key: "YYYY-WXX"

        self.load_all()

    def _get_path(self, table_name: str) -> str:
        return os.path.join(self.tables_dir, f"{table_name}.yaml")

    def _get_week_path(self, year: int, week_num: int) -> str:
        return os.path.join(self.weeks_dir, f"{year}-W{week_num:02d}.yaml")

    def load_all(self) -> None:
        """Carga todas las tablas de entidades desde el disco."""
        self.load_definitions()
        self.load_tasks()
        self.load_notes()

    def load_definitions(self) -> None:
        path = self._get_path("definitions")
        self.definitions.clear()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            items = data.get("definitions", [])
            for item in items:
                d = Definition.from_dict(item)
                if d.id:
                    self.definitions[d.id] = d

    def load_tasks(self) -> None:
        path = self._get_path("tasks")
        self.tasks.clear()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            items = data.get("tasks", [])
            for item in items:
                t = Task.from_dict(item)
                if t.id:
                    self.tasks[t.id] = t

    def load_notes(self) -> None:
        path = self._get_path("notes")
        self.notes.clear()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            items = data.get("notes", [])
            for item in items:
                n = Note.from_dict(item)
                if n.id:
                    self.notes[n.id] = n

    def save_definitions(self) -> None:
        path = self._get_path("definitions")
        data = {"definitions": [d.to_dict() for d in self.definitions.values()]}
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    def save_tasks(self) -> None:
        path = self._get_path("tasks")
        data = {"tasks": [t.to_dict() for t in self.tasks.values()]}
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    def save_notes(self) -> None:
        path = self._get_path("notes")
        data = {"notes": [n.to_dict() for n in self.notes.values()]}
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    def load_week(self, year: int, week_num: int, reload: bool = False) -> Optional[WeekSchedule]:
        """Carga la estructura de una semana específica."""
        key = f"{year}-W{week_num:02d}"
        if not reload and key in self.weeks:
            return self.weeks[key]

        path = self._get_week_path(year, week_num)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        week = WeekSchedule.from_dict(data)
        self.weeks[key] = week
        return week

    def save_week(self, schedule: WeekSchedule) -> None:
        """Guarda la estructura de una semana en YAML."""
        key = f"{schedule.year}-W{schedule.week_number:02d}"
        path = self._get_week_path(schedule.year, schedule.week_number)
        data = schedule.to_dict()
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        self.weeks[key] = schedule

    def save_all(self) -> None:
        """Persiste todas las tablas en disco."""
        self.save_definitions()
        self.save_tasks()
        self.save_notes()
        for week in self.weeks.values():
            self.save_week(week)

    # -------------------------------------------------------------------------
    # Métodos de Negocio: Tareas
    # -------------------------------------------------------------------------
    def create_task(
        self,
        title: str,
        status: str = "pending",
        definition_ids: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        year: Optional[int] = None,
        week_num: Optional[int] = None,
        day_number: Optional[int] = None,
        is_topic: bool = False
    ) -> Task:
        """Crea una tarea, la registra en la tabla y opcionalmente la vincula a la semana/día."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        if not task_id:
            # Generar ID incremental simple basado en timestamp/conteo
            count = len(self.tasks) + 1
            task_id = f"TSK-{count:04d}"

        task = Task(
            id=task_id,
            title=title.strip(),
            status=status,
            created_at=today_str,
            completed_at=today_str if status == "done" else None,
            definition_ids=definition_ids or [],
            project_id=project_id
        )

        self.tasks[task_id] = task
        self.save_tasks()

        # Vincular a la semana si se especifican los parámetros
        if year and week_num:
            week = self.load_week(year, week_num)
            if week:
                if is_topic:
                    if task_id not in week.topics_task_ids:
                        week.topics_task_ids.append(task_id)
                elif day_number:
                    for d in week.days:
                        if d.day_number == day_number:
                            if task_id not in d.task_ids:
                                d.task_ids.append(task_id)
                            break
                self.save_week(week)

        return task

    def toggle_task(self, task_id: str) -> Optional[Task]:
        """Alterna el estado de una tarea entre 'pending' y 'done'."""
        task = self.tasks.get(task_id)
        if not task:
            return None

        today_str = datetime.now().strftime("%Y-%m-%d")
        if task.is_done:
            task.status = "pending"
            task.completed_at = None
        else:
            task.status = "done"
            task.completed_at = today_str

        self.save_tasks()
        return task

    def delete_task(
        self,
        task_id: str,
        year: Optional[int] = None,
        week_num: Optional[int] = None,
        day_number: Optional[int] = None
    ) -> bool:
        """Elimina una tarea de la tabla o desvincula del día de la semana."""
        if task_id not in self.tasks:
            return False

        # Desvincular de la semana si existe
        if year and week_num:
            week = self.load_week(year, week_num)
            if week:
                if task_id in week.topics_task_ids:
                    week.topics_task_ids.remove(task_id)
                if day_number:
                    for d in week.days:
                        if d.day_number == day_number and task_id in d.task_ids:
                            d.task_ids.remove(task_id)
                self.save_week(week)

        del self.tasks[task_id]
        self.save_tasks()
        return True

    # -------------------------------------------------------------------------
    # Métodos de Negocio: Definiciones
    # -------------------------------------------------------------------------
    def ensure_definition(self, def_id: str, url: str, title: Optional[str] = None) -> Definition:
        """Garantiza que una definición exista en la tabla."""
        if def_id in self.definitions:
            return self.definitions[def_id]

        def_obj = Definition(id=def_id, url=url, title=title)
        self.definitions[def_id] = def_obj
        self.save_definitions()
        return def_obj

    def ensure_jira_definition(
        self,
        ticket_code: str,
        base_url: str = "https://mangospain.atlassian.net/browse/"
    ) -> Definition:
        """Normaliza un ticket de Jira (ej: ATLM-12703 -> [🎫ATLM-12703]) y asegura su URL."""
        clean_code = ticket_code.replace("[", "").replace("]", "").replace("🎫", "").strip()
        formatted_id = f"[🎫{clean_code}]"
        full_url = f"{base_url}{clean_code}"
        return self.ensure_definition(def_id=formatted_id, url=full_url, title=clean_code)

    # -------------------------------------------------------------------------
    # Métodos de Negocio: Notas
    # -------------------------------------------------------------------------
    def add_note(
        self,
        content: List[str] | str,
        year: int,
        week_num: int,
        note_id: Optional[str] = None,
        title: Optional[str] = None
    ) -> Note:
        """Crea una nota y la asocia a la semana indicada."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        if not note_id:
            note_id = f"NOTE-{len(self.notes) + 1:04d}"

        if isinstance(content, str):
            content_list = [content]
        else:
            content_list = list(content)

        note = Note(
            id=note_id,
            content=content_list,
            title=title,
            created_at=today_str
        )
        self.notes[note_id] = note
        self.save_notes()

        week = self.load_week(year, week_num)
        if week:
            if note_id not in week.note_ids:
                week.note_ids.append(note_id)
            self.save_week(week)

        return note
