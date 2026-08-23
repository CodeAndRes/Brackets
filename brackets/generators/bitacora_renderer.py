#!/usr/bin/env python3
"""
Motor de Renderizado: Traduce entidades relacionales (YAML) a Markdown oficial de Bitácoras.
"""

from __future__ import annotations
import re
from typing import Set, List
from brackets.models.entities import WeekSchedule, Task, Note, Definition
from brackets.managers.entity_manager import EntityManager
from brackets.utils.legacy_utils import safe_file_write


class BitacoraRenderer:
    """Renderiza estructuras de semana relacionales en archivos Markdown limpios."""

    @staticmethod
    def render_week(schedule: WeekSchedule, manager: EntityManager) -> str:
        """Genera el contenido Markdown completo para una semana."""
        lines: List[str] = []
        used_def_ids: Set[str] = set()

        # 1. Encabezado principal
        weight_str = f" {schedule.weight}" if schedule.weight else ""
        lines.append(f"# 🗓️Week {schedule.week_number}{weight_str}\n")

        # 2. Sección Topics
        lines.append("## ✅Topics")
        if schedule.topics_task_ids:
            for task_id in schedule.topics_task_ids:
                task = manager.tasks.get(task_id)
                if not task:
                    continue
                lines.append(BitacoraRenderer._format_task_line(task))
                used_def_ids.update(BitacoraRenderer._extract_definition_ids(task.title))
        else:
            lines.append("  - [ ] ")
        lines.append("  ---\n")

        # 3. Sección Notes
        lines.append("## 📝Notes")
        if schedule.note_ids:
            for note_id in schedule.note_ids:
                note = manager.notes.get(note_id)
                if not note:
                    continue
                if note.title:
                    lines.append(f"- ### {note.title}")
                    used_def_ids.update(BitacoraRenderer._extract_definition_ids(note.title))
                    for content_line in note.content:
                        lines.append(f"  - {content_line}")
                        used_def_ids.update(BitacoraRenderer._extract_definition_ids(content_line))
                else:
                    for content_line in note.content:
                        lines.append(f"- {content_line}")
                        used_def_ids.update(BitacoraRenderer._extract_definition_ids(content_line))
        else:
            lines.append("  - ")
        lines.append("  ---\n")

        # 4. Secciones Diarias
        for day in schedule.days:
            note_suffix = f" ({day.location_note})" if day.location_note else ""
            lines.append(f"## {day.location_emoji}{day.day_number}{note_suffix}")
            if day.task_ids:
                for task_id in day.task_ids:
                    task = manager.tasks.get(task_id)
                    if not task:
                        continue
                    lines.append(BitacoraRenderer._format_task_line(task))
                    used_def_ids.update(BitacoraRenderer._extract_definition_ids(task.title))
            else:
                lines.append("  - ")
            lines.append("")

        # 5. Sección Definiciones (al pie)
        # Resolver todas las definiciones usadas
        definitions_to_render: List[Definition] = []
        for def_id in sorted(used_def_ids):
            # Normalizar para buscar en manager
            def_obj = manager.definitions.get(def_id)
            if def_obj:
                definitions_to_render.append(def_obj)

        if definitions_to_render:
            lines.append("<!-- Definiciones -->")
            for d in definitions_to_render:
                lines.append(f"{d.id}: {d.url}")

        return "\n".join(lines).strip() + "\n"

    @staticmethod
    def _format_task_line(task: Task) -> str:
        """Formatea la línea de tarea según su estado."""
        if task.is_done:
            return f"  - [x] {task.title}"
        elif task.is_cancelled:
            # Si no tiene ya tildes en el título, envolver
            if "~~" not in task.title:
                return f"  - [ ] ~~{task.title}~~"
            return f"  - [ ] {task.title}"
        else:
            return f"  - [ ] {task.title}"

    @staticmethod
    def _extract_definition_ids(text: str) -> Set[str]:
        """Detecta automáticamente IDs de definición tipo [🎫TICKET] o [🤖Agente] en el texto."""
        found: Set[str] = set()
        # Busca patrones tipo [🎫...] o [🦒...] o [🤖...]
        pattern = r'(\[(?:🎫|🦒|🤖|📺|🎫)[^\]]+\])'
        matches = re.findall(pattern, text)
        found.update(matches)
        return found

    @staticmethod
    def render_and_save_week(
        schedule: WeekSchedule,
        manager: EntityManager,
        target_filepath: str
    ) -> bool:
        """Renderiza y guarda el archivo Markdown en disco."""
        content = BitacoraRenderer.render_week(schedule, manager)
        return safe_file_write(target_filepath, content)
