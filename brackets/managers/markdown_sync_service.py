#!/usr/bin/env python3
"""
Servicio de Sincronización Bidireccional: Markdown ➔ YAML Database.
Analiza archivos Markdown editados externamente (Obsidian, VSCode, etc.)
y reconcilia el estado de tareas, notas e ideas en la base de datos relacional YAML.
Garantiza la no duplicidad de tareas arrastradas entre días.
"""

from __future__ import annotations
import os
import re
from datetime import datetime
from typing import Optional, List, Dict, Tuple, Any

from brackets.models.entities import Task, Note, Idea, WeekSchedule, DaySchedule
from brackets.managers.entity_manager import EntityManager


class MarkdownSyncService:
    """Reconcilia cambios hechos a mano en Markdown hacia la base de datos YAML."""

    def __init__(self, entity_manager: EntityManager, vault_root: str = "."):
        self.manager = entity_manager
        self.vault_root = os.path.abspath(vault_root)

    # -------------------------------------------------------------------------
    # Sincronización de Bitácora Semanal
    # -------------------------------------------------------------------------
    def sync_week_from_markdown(self, md_path: str, year: int, week_num: int) -> bool:
        """Lee un archivo Markdown de bitácora semanal y reconcilia tareas, notas y topics."""
        if not os.path.exists(md_path):
            return False

        week = self.manager.load_week(year, week_num)
        if not week:
            return False

        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        today_str = datetime.now().strftime("%Y-%m-%d")

        # 1. Parsear Secciones Principales
        sections = self._parse_markdown_sections(content)

        # 2. Reconciliar Topics (## ✅Topics)
        topics_lines = sections.get("topics", [])
        self._reconcile_topics(week, topics_lines, today_str)

        # 3. Reconciliar Notas (## 📝Notes)
        notes_blocks = sections.get("notes_blocks", [])
        self._reconcile_notes(week, notes_blocks, year, week_num)

        # 4. Reconciliar Días de forma holística sin duplicidades
        days_dict = sections.get("days", {})
        self._reconcile_all_days(week, days_dict, year, week_num, today_str)

        # Guardar cambios en YAML
        self.manager.save_tasks()
        self.manager.save_notes()
        self.manager.save_week(week)
        return True

    def _parse_markdown_sections(self, content: str) -> Dict[str, Any]:
        """Trocea el documento Markdown en sus secciones semánticas."""
        lines = content.splitlines()
        current_section = None
        current_day_num = None

        topics_lines: List[Tuple[bool, str]] = []
        notes_raw_lines: List[str] = []
        days: Dict[int, List[Tuple[bool, str]]] = {}

        for line in lines:
            stripped = line.strip()

            # Detectar encabezados nivel 2
            if stripped.startswith("## "):
                header = stripped[3:].strip()
                if "Topics" in header or "✅" in header:
                    current_section = "topics"
                    current_day_num = None
                    continue
                elif "Notes" in header or "📝" in header:
                    current_section = "notes"
                    current_day_num = None
                    continue
                else:
                    # Buscar número de día en el encabezado (ej: "🏠24", "🚗 25", "26")
                    match = re.search(r'\b(\d{1,2})\b', header)
                    if match:
                        current_section = "day"
                        current_day_num = int(match.group(1))
                        days.setdefault(current_day_num, [])
                        continue
                    else:
                        current_section = None
                        current_day_num = None
                        continue

            if not stripped or stripped.startswith("---"):
                continue

            if current_section == "topics":
                m = re.match(r'^\s*-\s*\[([ xX])\]\s*(.*)$', line)
                if m:
                    is_done = m.group(1).lower() == 'x'
                    t_text = m.group(2).strip()
                    if t_text:
                        topics_lines.append((is_done, t_text))
            elif current_section == "notes":
                notes_raw_lines.append(line)
            elif current_section == "day" and current_day_num is not None:
                m = re.match(r'^\s*-\s*\[([ xX])\]\s*(.*)$', line)
                if m:
                    is_done = m.group(1).lower() == 'x'
                    t_text = m.group(2).strip()
                    if t_text:
                        days[current_day_num].append((is_done, t_text))
                elif line.strip().startswith("- "):
                    # Tarea sin checkbox explícito
                    t_text = line.strip()[2:].strip()
                    if t_text:
                        days[current_day_num].append((False, t_text))

        # Parsear bloques de notas a partir de notes_raw_lines
        notes_blocks = self._parse_notes_blocks(notes_raw_lines)

        return {
            "topics": topics_lines,
            "notes_blocks": notes_blocks,
            "days": days
        }

    def _parse_notes_blocks(self, raw_lines: List[str]) -> List[Dict[str, Any]]:
        """Extrae bloques de notas con subencabezados (### Título o - ### Título) y sus viñetas."""
        blocks: List[Dict[str, Any]] = []
        current_title = None
        current_proj = None
        current_bullets: List[str] = []

        for line in raw_lines:
            stripped = line.strip()
            if stripped.startswith("### ") or stripped.startswith("- ### "):
                if current_title or current_bullets:
                    blocks.append({
                        "title": current_title,
                        "project_id": current_proj,
                        "content": current_bullets
                    })
                if stripped.startswith("- ### "):
                    header = stripped[6:].strip()
                else:
                    header = stripped[4:].strip()

                # Extraer proyecto si está presente como [PROJ] Título
                p_match = re.match(r'^\[([A-Za-z0-9_-]+)\]\s*(.*)$', header)
                if p_match:
                    current_proj = p_match.group(1).strip()
                    current_title = p_match.group(2).strip()
                else:
                    current_proj = None
                    current_title = header
                current_bullets = []
            elif stripped.startswith("- "):
                bullet = stripped[2:].strip()
                if bullet:
                    current_bullets.append(bullet)

        if current_title or current_bullets:
            blocks.append({
                "title": current_title,
                "project_id": current_proj,
                "content": current_bullets
            })

        return blocks

    def _reconcile_topics(self, week: WeekSchedule, topic_tuples: List[Tuple[bool, str]], today_str: str) -> None:
        """Reconcilia la lista de topics con los tasks en YAML."""
        current_tasks = [self.manager.tasks[tid] for tid in week.topics_task_ids if tid in self.manager.tasks]

        for is_done, title in topic_tuples:
            # Buscar tarea existente por título
            matched_task = next((t for t in current_tasks if t.title == title), None)
            if matched_task:
                if matched_task.is_done != is_done:
                    matched_task.status = "done" if is_done else "pending"
                    matched_task.completed_at = today_str if is_done else None
            else:
                # Tarea añadida a mano en Topics
                new_task = self.manager.create_task(title=title)
                if is_done:
                    new_task.status = "done"
                    new_task.completed_at = today_str
                self.manager.add_topic_to_week(week, new_task.id)

    def _reconcile_notes(self, week: WeekSchedule, note_blocks: List[Dict[str, Any]], year: int, week_num: int) -> None:
        """Reconcilia bloques de notas editados a mano."""
        existing_notes = [self.manager.notes[nid] for nid in week.note_ids if nid in self.manager.notes]

        for block in note_blocks:
            title = block.get("title")
            proj = block.get("project_id")
            bullets = block.get("content", [])

            # Buscar nota existente
            matched_note = None
            for n in existing_notes:
                if title and n.title and n.title.strip().lower() == title.strip().lower():
                    matched_note = n
                    break

            if matched_note:
                # Actualizar viñetas y proyecto si cambiaron
                if bullets:
                    matched_note.content = list(bullets)
                if proj:
                    matched_note.project_id = proj
            else:
                # Nota creada a mano en el markdown
                if title or bullets:
                    self.manager.add_note(
                        title=title,
                        content=bullets,
                        project_id=proj,
                        year=year,
                        week_num=week_num
                    )

    def _reconcile_all_days(
        self,
        week: WeekSchedule,
        days_dict: Dict[int, List[Tuple[bool, str]]],
        year: int,
        week_num: int,
        today_str: str
    ) -> None:
        """
        Reconcilia tareas de todos los días de la semana de forma holística:
        - Si una tarea está completada ([x]), se asigna al día donde se completó y se marca done.
        - Si una tarea está pendiente ([ ]):
            - Si aparece en múltiples días en el markdown (por haber sido arrastrada previamente),
              SOLO se asigna al ÚLTIMO día donde aparece (o día activo).
            - Se elimina de los días anteriores de la semana para evitar duplicidades.
        - Se limpia cualquier ID duplicado dentro del mismo día o entre días para tareas pendientes.
        """
        day_by_number = {d.day_number: d for d in week.days}
        ordered_day_numbers = [d.day_number for d in week.days]

        pending_task_latest_day: Dict[str, int] = {}
        done_tasks_by_day: Dict[int, List[str]] = {d_num: [] for d_num in ordered_day_numbers}

        for day_num in ordered_day_numbers:
            tuples = days_dict.get(day_num, [])
            for is_done, title in tuples:
                clean_title = title.strip()
                if not clean_title:
                    continue
                if is_done:
                    done_tasks_by_day.setdefault(day_num, []).append(clean_title)
                else:
                    # Guardar el último día donde aparece como pendiente
                    pending_task_latest_day[clean_title] = day_num

        # 1. Reconciliar tareas COMPLETADAS ([x])
        for day_num, done_titles in done_tasks_by_day.items():
            day = day_by_number.get(day_num)
            if not day:
                continue
            for title in done_titles:
                matched_task = next((t for t in self.manager.tasks.values() if t.title == title), None)
                if not matched_task:
                    matched_task = self.manager.create_task(
                        title=title,
                        year=year,
                        week_num=week_num,
                        day_number=day_num,
                        status="done"
                    )
                else:
                    matched_task.status = "done"
                    if not matched_task.completed_at:
                        matched_task.completed_at = today_str

                if matched_task.id not in day.task_ids:
                    day.task_ids.append(matched_task.id)

        # 2. Reconciliar tareas PENDIENTES ([ ])
        for title, latest_day_num in pending_task_latest_day.items():
            target_day = day_by_number.get(latest_day_num)
            if not target_day:
                continue

            matched_task = next((t for t in self.manager.tasks.values() if t.title == title), None)
            if not matched_task:
                matched_task = self.manager.create_task(
                    title=title,
                    year=year,
                    week_num=week_num,
                    day_number=latest_day_num,
                    status="pending"
                )

            # Asegurar que esté en el latest_day
            if matched_task.id not in target_day.task_ids:
                target_day.task_ids.append(matched_task.id)

            # ELIMINAR de todos los días distintos a latest_day_num para evitar duplicidades
            for d_num in ordered_day_numbers:
                if d_num != latest_day_num:
                    other_day = day_by_number.get(d_num)
                    if other_day and matched_task.id in other_day.task_ids:
                        if matched_task.is_pending:
                            other_day.task_ids.remove(matched_task.id)

        # 3. Deduplicar IDs en cada día preservando orden
        for day in week.days:
            seen = set()
            deduped = []
            for tid in day.task_ids:
                if tid not in seen and tid in self.manager.tasks:
                    seen.add(tid)
                    deduped.append(tid)
            day.task_ids = deduped

    # -------------------------------------------------------------------------
    # Sincronización de Ideas ([🧩GENERAL]🧠Ideas.md)
    # -------------------------------------------------------------------------
    def sync_ideas_from_markdown(self, md_path: str) -> bool:
        """Lee [🧩GENERAL]🧠Ideas.md y reconcilia estado y viñetas en ideas.yaml."""
        if not os.path.exists(md_path):
            return False

        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.splitlines()
        current_project = None
        current_idea_title = None
        current_idea_status = "evaluating"
        current_idea_bullets: List[str] = []

        parsed_ideas: List[Dict[str, Any]] = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## 📁 "):
                # Guardar idea previa
                if current_idea_title:
                    parsed_ideas.append({
                        "title": current_idea_title,
                        "project_id": current_project,
                        "status": current_idea_status,
                        "content": current_idea_bullets
                    })
                    current_idea_title = None
                    current_idea_bullets = []

                p_str = stripped[5:].strip()
                current_project = None if p_str == "GENERAL" else p_str
                continue

            # Detectar idea (checkbox)
            m = re.match(r'^\s*-\s*\[([ xX])\]\s*(.*)$', line)
            if m and not line.startswith("    ") and not line.startswith("\t"):
                if current_idea_title:
                    parsed_ideas.append({
                        "title": current_idea_title,
                        "project_id": current_project,
                        "status": current_idea_status,
                        "content": current_idea_bullets
                    })

                box = m.group(1).lower()
                raw_text = m.group(2).strip()

                if "~~" in raw_text:
                    current_idea_status = "discarded"
                    current_idea_title = raw_text.replace("~~", "").strip()
                elif box == "x":
                    current_idea_status = "accepted"
                    current_idea_title = raw_text
                else:
                    current_idea_status = "evaluating"
                    current_idea_title = raw_text

                current_idea_bullets = []
                continue

            # Viñeta indentada de hipótesis
            if (line.startswith("  - ") or line.startswith("    - ")) and current_idea_title:
                bullet = stripped[2:].strip()
                if bullet:
                    current_idea_bullets.append(bullet)

        if current_idea_title:
            parsed_ideas.append({
                "title": current_idea_title,
                "project_id": current_project,
                "status": current_idea_status,
                "content": current_idea_bullets
            })

        # Reconciliar ideas en EntityManager
        for item in parsed_ideas:
            t = item["title"]
            proj = item["project_id"]
            stat = item["status"]
            bullets = item["content"]

            matched_idea = next(
                (i for i in self.manager.ideas.values() if i.title == t and i.project_id == proj),
                None
            )
            if matched_idea:
                matched_idea.status = stat
                if bullets:
                    matched_idea.content = list(bullets)
            else:
                self.manager.create_idea(
                    title=t,
                    content=bullets,
                    project_id=proj,
                    status=stat
                )

        self.manager.save_ideas()
        return True
