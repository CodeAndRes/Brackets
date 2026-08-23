#!/usr/bin/env python3
"""
Constructor del Dataset Mock 2026 Completo para Brackets.
Analiza todas las bitácoras semanales de 2026 en MyJobNotes, deduplica tareas con
trazabilidad de ciclo de vida (created_at / completed_at / status), extrae notas,
definiciones y proyectos, y genera las tablas relacionales en data/mock/.
"""

import os
import re
import glob
from datetime import datetime, date
from typing import Dict, List, Set, Optional, Tuple, Any
import yaml


class Mock2026Builder:
    def __init__(self, notes_dir: str, output_dir: str):
        self.notes_dir = os.path.abspath(notes_dir)
        self.output_dir = os.path.abspath(output_dir)
        self.tables_dir = os.path.join(self.output_dir, "tables")
        self.weeks_dir = os.path.join(self.output_dir, "weeks")

        os.makedirs(self.tables_dir, exist_ok=True)
        os.makedirs(self.weeks_dir, exist_ok=True)

        self.tasks: Dict[str, Dict[str, Any]] = {}  # key: task_id
        self.task_canonical_map: Dict[str, str] = {}  # canonical_text -> task_id
        self.notes: Dict[str, Dict[str, Any]] = {}  # key: note_id
        self.note_canonical_map: Dict[str, str] = {}  # canonical_text -> note_id
        self.definitions: Dict[str, Dict[str, Any]] = {}  # key: def_id
        self.weeks: Dict[str, Dict[str, Any]] = {}  # key: YYYY-WXX

        self.task_counter = 0
        self.note_counter = 0

    def _canonical(self, text: str) -> str:
        """Normaliza texto para deduplicación."""
        t = re.sub(r'~~', '', text)
        t = re.sub(r'\[[ xX]\]', '', t)
        t = re.sub(r'^\s*[-*•#\d\.]+\s*', '', t)
        return " ".join(t.strip().lower().split())

    def _infer_project(self, title: str) -> Optional[str]:
        """Infiere el proyecto a partir de palabras clave."""
        t = title.upper()
        if "AMR" in t or "TGW" in t:
            return "AMR_LOGISTICS"
        if "ROVO" in t:
            return "ROVO_AI"
        if "INFLUXDB" in t or "GRAFANA" in t or "INFLUX" in t:
            return "METRICS_INFLUXDB"
        if "EXPORT" in t or "ATLM" in t or "JIRA" in t:
            return "JIRA_EXPORT"
        if "KOERBER" in t or "KÖRBER" in t:
            return "KOERBER_E2E"
        if "QOREX" in t:
            return "QOREX_DB"
        if "COPILOT" in t or "MS-COPILOT" in t:
            return "MS_COPILOT"
        if "CARDINAL" in t:
            return "CARDINAL"
        if "NCM" in t:
            return "NCM_DASHBOARD"
        if "BRACKETS" in t or "BITACORA" in t:
            return "BRACKETS_SYSTEM"
        return "GENERAL"

    def _extract_definitions(self, text: str) -> List[str]:
        """Extrae identificadores de definiciones."""
        found = []
        # Buscar formato [🎫ATLM-12345] o [🦒...] o [🤖...] o [📺...]
        matches = re.findall(r'(\[(?:🎫|🦒|🤖|📺)[^\]]+\])', text)
        for m in matches:
            found.append(m)
            if m not in self.definitions:
                clean = m.replace("[", "").replace("]", "").replace("🎫", "").replace("🦒", "").replace("🤖", "").replace("📺", "").strip()
                url = f"https://mangospain.atlassian.net/browse/{clean}" if "ATLM" in clean or "SYSC" in clean or "OPSC" in clean else "https://atlassian.net"
                self.definitions[m] = {
                    "id": m,
                    "url": url,
                    "title": clean,
                    "type": "jira" if "ATLM" in clean or "SYSC" in clean or "OPSC" in clean else "link"
                }

        # Buscar también formato directo 🎫ATLM-12345
        raw_jira = re.findall(r'🎫([A-Z]+-\d+)', text)
        for rj in raw_jira:
            fid = f"[🎫{rj}]"
            if fid not in found:
                found.append(fid)
            if fid not in self.definitions:
                self.definitions[fid] = {
                    "id": fid,
                    "url": f"https://mangospain.atlassian.net/browse/{rj}",
                    "title": rj,
                    "type": "jira"
                }
        return found

    def process_all_weeks(self):
        """Lee y procesa todas las bitácoras de 2026 en orden cronológico."""
        files = []
        for item in os.listdir(self.notes_dir):
            if item.startswith("[2026]") and "Week" in item and item.endswith(".md"):
                files.append(os.path.join(self.notes_dir, item))

        # Ordenar por número de semana
        def get_week_key(fpath):
            fname = os.path.basename(fpath)
            match = re.search(r'\[2026\]\[(\d+)\]Week(\d+)', fname)
            if match:
                return (int(match.group(1)), int(match.group(2)))
            return (99, 999)

        files.sort(key=get_week_key)
        print(f"📂 Procesando {len(files)} archivos semanales de 2026...")

        for fpath in files:
            self._process_single_week(fpath)

        self._save_all()

    def _process_single_week(self, fpath: str):
        fname = os.path.basename(fpath)
        match = re.search(r'\[(\d{4})\]\[(\d{2})\]Week(\d+)', fname)
        if not match:
            return

        year = int(match.group(1))
        month = int(match.group(2))
        week_num = int(match.group(3))
        week_key = f"{year}-W{week_num:02d}"

        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Extraer peso
        weight = None
        weight_match = re.search(r'^# 🗓️Week \d+\s+([\d\.]+)', content, re.MULTILINE)
        if weight_match:
            try:
                weight = float(weight_match.group(1))
            except ValueError:
                pass

        # Extraer definiciones del pie
        def_footer_match = re.search(r'<!-- Definiciones -->(.*)', content, re.DOTALL)
        if def_footer_match:
            footer_text = def_footer_match.group(1)
            for line in footer_text.strip().split("\n"):
                def_line_match = re.match(r'^\s*(\[[^\]]+\]):\s*(\S+)', line.strip())
                if def_line_match:
                    did, durl = def_line_match.group(1), def_line_match.group(2)
                    clean_t = did.replace("[", "").replace("]", "").replace("🎫", "").strip()
                    self.definitions[did] = {
                        "id": did,
                        "url": durl,
                        "title": clean_t,
                        "type": "jira" if "atlassian" in durl else "link"
                    }

        # Extraer secciones
        topics_task_ids = []
        note_ids = []
        days_list = []

        # 1. Topics
        topics_match = re.search(r'## ✅Topics\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        if topics_match:
            topics_content = topics_match.group(1)
            for line in topics_content.split("\n"):
                line = line.strip()
                if not line or line.startswith("---"):
                    continue
                task_id = self._register_or_update_task(line, year, month, week_num, day_number=None, is_topic=True)
                if task_id and task_id not in topics_task_ids:
                    topics_task_ids.append(task_id)

        # 2. Notes
        notes_match = re.search(r'## 📝Notes\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        if notes_match:
            notes_content = notes_match.group(1)
            raw_lines = notes_content.split("\n")
            current_title = None
            current_content = []

            for line in raw_lines:
                sline = line.strip()
                if not sline or sline.startswith("---"):
                    continue

                if sline.startswith("- ### ") or sline.startswith("### "):
                    if current_title or current_content:
                        nid = self._register_note(current_title, current_content, year, month, week_num)
                        if nid and nid not in note_ids:
                            note_ids.append(nid)
                        current_title = None
                        current_content = []

                    if sline.startswith("- ### "):
                        current_title = sline[6:].strip()
                    else:
                        current_title = sline[4:].strip()

                elif sline.startswith("- ") or sline.startswith("• ") or sline.startswith("* "):
                    clean_l = re.sub(r'^[-*•]\s*', '', sline).strip()
                    if current_title is not None:
                        current_content.append(clean_l)
                    else:
                        if current_content:
                            nid = self._register_note(None, current_content, year, month, week_num)
                            if nid and nid not in note_ids:
                                note_ids.append(nid)
                            current_content = []
                        current_content.append(clean_l)
                else:
                    if current_content:
                        current_content.append(sline)
                    elif current_title:
                        current_content.append(sline)
                    else:
                        current_content.append(sline)

            if current_title or current_content:
                nid = self._register_note(current_title, current_content, year, month, week_num)
                if nid and nid not in note_ids:
                    note_ids.append(nid)

        # 3. Días
        day_sections = re.findall(r'## ([🚗🏠🏖️✈️🏢🏢🚲🚌🏥]+)\s*(\d+)(?:\s*\(([^)]+)\))?\s*\n(.*?)(?=\n## |<!-- Definiciones -->|\Z)', content, re.DOTALL)
        for emoji, day_num_str, note_opt, day_body in day_sections:
            day_num = int(day_num_str)
            day_task_ids = []
            for line in day_body.split("\n"):
                line = line.strip()
                if not line or line.startswith("---"):
                    continue
                task_id = self._register_or_update_task(line, year, month, week_num, day_number=day_num, is_topic=False)
                if task_id and task_id not in day_task_ids:
                    day_task_ids.append(task_id)

            days_list.append({
                "day_number": day_num,
                "location_emoji": emoji,
                "location_note": note_opt.strip() if note_opt else None,
                "task_ids": day_task_ids
            })

        self.weeks[week_key] = {
            "year": year,
            "month": month,
            "week_number": week_num,
            "weight": weight,
            "topics_task_ids": topics_task_ids,
            "note_ids": note_ids,
            "days": days_list
        }

    def _register_or_update_task(self, raw_line: str, year: int, month: int, week_num: int, day_number: Optional[int], is_topic: bool) -> Optional[str]:
        """Registra o actualiza una tarea deduplicada con trazabilidad temporal."""
        # Limpiar prefijos
        clean_text = raw_line.strip()
        is_done = False
        is_cancelled = False

        if clean_text.startswith("- [x]") or clean_text.startswith("- [X]"):
            is_done = True
            clean_text = clean_text[5:].strip()
        elif clean_text.startswith("- [ ]"):
            clean_text = clean_text[5:].strip()
        elif clean_text.startswith("- "):
            clean_text = clean_text[2:].strip()

        if clean_text.startswith("~~") and clean_text.endswith("~~"):
            is_cancelled = True
            clean_text = clean_text[2:-2].strip()
        elif "~~" in clean_text:
            is_cancelled = True
            clean_text = clean_text.replace("~~", "").strip()

        if not clean_text:
            return None

        # Fecha estimada
        if day_number:
            date_str = f"{year}-{month:02d}-{day_number:02d}"
        else:
            date_str = f"{year}-{month:02d}-01"

        canon = self._canonical(clean_text)
        if not canon:
            return None

        # Extraer definiciones
        defs = self._extract_definitions(clean_text)

        if canon in self.task_canonical_map:
            task_id = self.task_canonical_map[canon]
            task = self.tasks[task_id]

            if is_done:
                task["status"] = "done"
                task["completed_at"] = date_str
            elif is_cancelled:
                task["status"] = "cancelled"
            return task_id
        else:
            self.task_counter += 1
            task_id = f"TSK-{self.task_counter:04d}"
            status = "done" if is_done else ("cancelled" if is_cancelled else "pending")

            self.tasks[task_id] = {
                "id": task_id,
                "title": clean_text,
                "status": status,
                "created_at": date_str,
                "completed_at": date_str if is_done else None,
                "project_id": self._infer_project(clean_text)
            }
            self.task_canonical_map[canon] = task_id
            return task_id

    def _register_note(self, title: Optional[str], content_lines: List[str], year: int, month: int, week_num: int) -> Optional[str]:
        """Registra una nota estructurada con título y contenido deduplicada."""
        full_text = f"{title or ''} " + " ".join(content_lines)
        canon = self._canonical(full_text)
        if not canon:
            return None

        if title:
            self._extract_definitions(title)
        for line in content_lines:
            self._extract_definitions(line)

        if canon in self.note_canonical_map:
            return self.note_canonical_map[canon]

        self.note_counter += 1
        note_id = f"NOTE-{self.note_counter:04d}"
        month_str = f"{year}-{month:02d}"
        date_str = f"{year}-{month:02d}-01"
        project_id = self._infer_project(full_text)

        self.notes[note_id] = {
            "id": note_id,
            "title": title,
            "content": content_lines,
            "created_at": date_str,
            "month": month_str,
            "week": week_num,
            "project_id": project_id
        }
        self.note_canonical_map[canon] = note_id
        return note_id

    def _save_all(self):
        """Guarda todas las tablas y semanas en YAML."""
        print(f"\n💾 Guardando tablas en {self.output_dir}...")
        print(f"  • Total Tareas únicas: {len(self.tasks)}")
        print(f"  • Total Notas únicas: {len(self.notes)}")
        print(f"  • Total Definiciones: {len(self.definitions)}")
        print(f"  • Total Semanas procesadas: {len(self.weeks)}")

        # 1. tasks.yaml
        with open(os.path.join(self.tables_dir, "tasks.yaml"), "w", encoding="utf-8") as f:
            yaml.dump({"tasks": list(self.tasks.values())}, f, allow_unicode=True, sort_keys=False)

        # 2. notes/ {YYYY}-{MM}.yaml y notes.yaml
        notes_dir = os.path.join(self.tables_dir, "notes")
        os.makedirs(notes_dir, exist_ok=True)
        for old_f in glob.glob(os.path.join(notes_dir, "*.yaml")):
            try:
                os.remove(old_f)
            except Exception:
                pass

        grouped_notes: Dict[str, List[Dict[str, Any]]] = {}
        for n in self.notes.values():
            m = n.get("month", "general")
            grouped_notes.setdefault(m, []).append(n)

        for m_key, n_list in grouped_notes.items():
            m_file = os.path.join(notes_dir, f"{m_key}.yaml")
            with open(m_file, "w", encoding="utf-8") as f:
                yaml.dump({"notes": n_list}, f, allow_unicode=True, sort_keys=False)

        with open(os.path.join(self.tables_dir, "notes.yaml"), "w", encoding="utf-8") as f:
            yaml.dump({"notes": list(self.notes.values())}, f, allow_unicode=True, sort_keys=False)

        # 3. definitions.yaml
        with open(os.path.join(self.tables_dir, "definitions.yaml"), "w", encoding="utf-8") as f:
            yaml.dump({"definitions": list(self.definitions.values())}, f, allow_unicode=True, sort_keys=False)

        # 4. projects.yaml
        projects_summary: Dict[str, Dict[str, Any]] = {}
        for t in self.tasks.values():
            pid = t.get("project_id", "GENERAL")
            if pid not in projects_summary:
                projects_summary[pid] = {
                    "id": pid,
                    "name": pid.replace("_", " ").title()
                }

        with open(os.path.join(self.tables_dir, "projects.yaml"), "w", encoding="utf-8") as f:
            yaml.dump({"projects": list(projects_summary.values())}, f, allow_unicode=True, sort_keys=False)

        # 5. weeks/*.yaml
        for wkey, wdata in self.weeks.items():
            wpath = os.path.join(self.weeks_dir, f"{wkey}.yaml")
            with open(wpath, "w", encoding="utf-8") as f:
                yaml.dump(wdata, f, allow_unicode=True, sort_keys=False)

        print("✅ Base de datos mock de 2026 generada con éxito.")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    my_job_notes = os.path.abspath(os.path.join(base_dir, "..", "MyJobNotes"))
    mock_out = os.path.join(base_dir, "data", "mock")

    builder = Mock2026Builder(notes_dir=my_job_notes, output_dir=mock_out)
    builder.process_all_weeks()
