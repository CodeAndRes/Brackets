"""
Event Log: registro append-only de eventos de actividad.

Almacena un archivo YAML por día en data/log/YYYY-MM-DD.yaml.
Cada archivo contiene una lista de entries con timestamp y tipo de evento.
"""

import os
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import yaml


class EventLog:
    """Append-only event log con un archivo YAML por día."""

    def __init__(self, vault_root: str):
        """
        Args:
            vault_root: Ruta raíz del vault (directorio que contiene data/).
        """
        self.vault_root = os.path.abspath(vault_root)
        self.log_dir = os.path.join(self.vault_root, "data", "log")

    def _ensure_dir(self) -> None:
        """Crea el directorio de logs si no existe."""
        os.makedirs(self.log_dir, exist_ok=True)

    def _day_path(self, day: date) -> str:
        """Ruta al archivo de log para un día específico."""
        return os.path.join(self.log_dir, f"{day.isoformat()}.yaml")

    def append(self, event: str, **kwargs: Any) -> Dict[str, Any]:
        """Agrega un evento al log del día actual.

        Args:
            event: Tipo de evento (ej: "task_added", "pomodoro_start", "session_start").
            **kwargs: Datos adicionales del evento (task_id, task_text, detail, etc.).

        Returns:
            El entry completo que fue guardado.
        """
        self._ensure_dir()

        now = datetime.now()
        entry: Dict[str, Any] = {
            "ts": now.isoformat(timespec="seconds"),
            "event": event,
        }
        entry.update(kwargs)

        day_file = self._day_path(now.date())
        entries = self._load_entries(day_file)
        entries.append(entry)
        self._save_entries(day_file, entries)

        return entry

    def read_day(self, day: Optional[date] = None) -> List[Dict[str, Any]]:
        """Lee todos los eventos de un día.

        Args:
            day: Fecha a consultar. Si es None, usa hoy.

        Returns:
            Lista de entries del día (vacía si no hay archivo).
        """
        if day is None:
            day = date.today()
        day_file = self._day_path(day)
        return self._load_entries(day_file)

    def read_range(self, start: date, end: date) -> List[Dict[str, Any]]:
        """Lee eventos de un rango de días (inclusive).

        Args:
            start: Fecha inicial (inclusive).
            end: Fecha final (inclusive).

        Returns:
            Lista combinada de entries, ordenada cronológicamente.
        """
        all_entries: List[Dict[str, Any]] = []
        current = start
        while current <= end:
            all_entries.extend(self.read_day(current))
            current += timedelta(days=1)
        return all_entries

    def _load_entries(self, path: str) -> List[Dict[str, Any]]:
        """Carga entries de un archivo YAML."""
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict) and isinstance(data.get("entries"), list):
                return data["entries"]
            return []
        except (yaml.YAMLError, OSError):
            return []

    def _save_entries(self, path: str, entries: List[Dict[str, Any]]) -> None:
        """Guarda entries a un archivo YAML."""
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(
                {"entries": entries},
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
