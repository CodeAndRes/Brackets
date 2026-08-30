#!/usr/bin/env python3
"""
Script para generar el histórico mensual de actividad (2026-01.log a 2026-08.log)
a partir de las bitácoras y entidades reconstruidas de 2026.
"""

import os
import re
import glob
from datetime import datetime
import yaml

VAULT_ROOT = "c:/Projects/brackets-workspace/MyJobNotes"
DATA_DIR = os.path.join(VAULT_ROOT, "data")
TABLES_DIR = os.path.join(DATA_DIR, "tables")
NOTES_DIR = os.path.join(TABLES_DIR, "notes")
WEEKS_DIR = os.path.join(DATA_DIR, "weeks")
LOG_DIR = os.path.join(DATA_DIR, "log")

os.makedirs(LOG_DIR, exist_ok=True)

events_by_month = {}  # "YYYY-MM" -> list of (dt, line)

def add_event(dt, level, category, action, metadata_dict, message=""):
    month_key = f"{dt.year:04d}-{dt.month:02d}"
    ts_str = dt.strftime("%Y-%m-%d %H:%M:%S")

    meta_items = []
    for k, v in metadata_dict.items():
        if v is not None:
            val_str = str(v).replace("\n", " ").strip()
            meta_items.append(f"{k}={val_str}")
    meta_str = " | ".join(meta_items) if meta_items else ""

    parts = [f"[{ts_str}]", f"[{level.upper()}]", f"[{category.upper()}]", action]
    if meta_str:
        parts.append(f"| {meta_str}")
    if message:
        clean_msg = message.replace("\n", " ").strip()
        parts.append(f"| {clean_msg}")

    line = " ".join(parts)
    if month_key not in events_by_month:
        events_by_month[month_key] = []
    events_by_month[month_key].append((dt, line))

# 1. Cargar tareas de tasks.yaml
tasks_file = os.path.join(TABLES_DIR, "tasks.yaml")
if os.path.exists(tasks_file):
    with open(tasks_file, "r", encoding="utf-8") as f:
        tasks_data = yaml.safe_load(f)
    for t in tasks_data.get("tasks", []):
        tid = t.get("id")
        proj = t.get("project_id") or "POR_ASIGNAR"
        title = t.get("title", "")
        status = t.get("status")
        c_at = t.get("created_at")
        d_at = t.get("completed_at")
        due_scope = t.get("due_scope")

        # Evento de creación
        if c_at:
            try:
                dt_c = datetime.strptime(c_at, "%Y-%m-%d").replace(hour=9, minute=0, second=0)
                add_event(dt_c, "INFO", "TASK", "created", {"id": tid, "project": proj}, title)
            except Exception:
                pass

        # Evento de completado
        if status == "done" and d_at:
            try:
                dt_d = datetime.strptime(d_at, "%Y-%m-%d").replace(hour=17, minute=30, second=0)
                add_event(dt_d, "INFO", "TASK", "completed", {"id": tid, "project": proj}, title)
            except Exception:
                pass

        # Evento de migración al backlog
        if due_scope == "backlog" and c_at:
            try:
                dt_b = datetime.strptime(c_at, "%Y-%m-%d").replace(hour=18, minute=0, second=0)
                add_event(dt_b, "INFO", "TASK", "migrated_to_backlog", {"id": tid, "project": proj, "reason": "rollover_2_weeks"}, title)
            except Exception:
                pass

print(f"Cargadas tareas de {tasks_file}")

# 2. Cargar notas de notes/*.yaml
for note_path in glob.glob(os.path.join(NOTES_DIR, "*.yaml")):
    with open(note_path, "r", encoding="utf-8") as f:
        ndata = yaml.safe_load(f)
    for n in ndata.get("notes", []):
        nid = n.get("id")
        proj = n.get("project_id")
        title = n.get("title") or "Nota sin título"
        topic = n.get("topic_id")
        c_at = n.get("created_at")
        if c_at:
            try:
                dt_n = datetime.strptime(c_at, "%Y-%m-%d").replace(hour=11, minute=0, second=0)
                add_event(dt_n, "INFO", "NOTE", "created", {"id": nid, "project": proj, "topic": topic}, title)
            except Exception:
                pass

# 3. Cargar semanas
for w_path in glob.glob(os.path.join(WEEKS_DIR, "*.yaml")):
    with open(w_path, "r", encoding="utf-8") as f:
        wdata = yaml.safe_load(f)
    year = wdata.get("year", 2026)
    week_num = wdata.get("week_number")
    # Estimar fecha del lunes de esa semana
    try:
        dt_w = datetime.strptime(f"{year}-W{week_num:02d}-1", "%Y-W%W-%w").replace(hour=8, minute=30, second=0)
        add_event(dt_w, "INFO", "WEEK", "opened", {"week": f"W{week_num:02d}", "year": year}, f"Semana {week_num:02d} abierta")
    except Exception:
        pass

# 4. Cargar sesiones previas de los archivos 2026-WXX.yaml existentes
for log_yaml in glob.glob(os.path.join(LOG_DIR, "2026-W*.yaml")):
    try:
        with open(log_yaml, "r", encoding="utf-8") as f:
            ldata = yaml.safe_load(f)
        for entry in ldata.get("entries", []):
            ts_str = entry.get("ts")
            event = entry.get("event")
            vault = entry.get("vault", "MyJobNotes")
            if ts_str:
                dt_s = datetime.fromisoformat(ts_str)
                if event == "session_start":
                    add_event(dt_s, "INFO", "STARTUP", "run_brackets", {"vault": vault, "mode": "interactive"}, f"Sesión iniciada en vault '{vault}'")
                elif event == "bitacora_generated":
                    btype = entry.get("type", "weekly")
                    add_event(dt_s, "INFO", "BITACORA", "generated", {"type": btype}, f"Bitácora {btype} generada")
    except Exception:
        pass

# 5. Escribir cada archivo mensual ordenado cronológicamente
print("\n--- GENERANDO ARCHIVOS MENSUALES .log ---")
for month_key in sorted(events_by_month.keys()):
    month_events = events_by_month[month_key]
    month_events.sort(key=lambda x: x[0])

    log_filename = f"{month_key}.log"
    log_path = os.path.join(LOG_DIR, log_filename)

    with open(log_path, "w", encoding="utf-8") as f:
        for dt, line in month_events:
            f.write(line + "\n")

    print(f"  ✅ {log_filename}: {len(month_events)} eventos registrados")

print("\n🎉 Volcado histórico mensual completado exitosamente!")