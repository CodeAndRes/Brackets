#!/usr/bin/env python3
"""
Modelos de Entidad para la Arquitectura Relacional YAML-First de Brackets.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any


@dataclass
class Definition:
    """Entidad Definición / Enlace externo (Jira, Confluence, etc.)."""
    id: str  # ej: "🎫ATLM-12682" o "🦒EXPORT"
    url: str  # ej: "https://mangospain.atlassian.net/browse/ATLM-12682"
    title: Optional[str] = None
    type: str = "jira"  # "jira", "link", "custom"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Definition:
        return cls(
            id=data.get("id", ""),
            url=data.get("url", ""),
            title=data.get("title"),
            type=data.get("type", "jira")
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Task:
    """Entidad Tarea independiente con trazabilidad temporal."""
    id: str
    title: str
    status: str = "pending"  # "pending", "done", "cancelled"
    created_at: str = ""  # "YYYY-MM-DD"
    completed_at: Optional[str] = None
    definition_ids: List[str] = field(default_factory=list)
    project_id: Optional[str] = None
    parent_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    @property
    def is_done(self) -> bool:
        return self.status.lower() == "done"

    @property
    def is_cancelled(self) -> bool:
        return self.status.lower() == "cancelled"

    @property
    def is_pending(self) -> bool:
        return self.status.lower() == "pending"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Task:
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            status=data.get("status", "pending"),
            created_at=data.get("created_at", ""),
            completed_at=data.get("completed_at"),
            definition_ids=data.get("definition_ids", []),
            project_id=data.get("project_id"),
            parent_id=data.get("parent_id"),
            tags=data.get("tags", [])
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Note:
    """Entidad Nota de trabajo semanal."""
    id: str
    content: List[str] = field(default_factory=list)  # Líneas o viñetas de la nota
    title: Optional[str] = None
    created_at: str = ""
    project_ref: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Note:
        content_raw = data.get("content", [])
        if isinstance(content_raw, str):
            content_list = [content_raw]
        else:
            content_list = list(content_raw)
        return cls(
            id=data.get("id", ""),
            content=content_list,
            title=data.get("title"),
            created_at=data.get("created_at", ""),
            project_ref=data.get("project_ref")
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DaySchedule:
    """Configuración de un día dentro de la bitácora semanal."""
    day_number: int  # 17, 18, 19, etc.
    location_emoji: str = "🏠"  # 🏠, 🚗, 🏖️
    location_note: Optional[str] = None  # "Oficina", "Vacaciones"
    task_ids: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DaySchedule:
        return cls(
            day_number=int(data.get("day_number", 0)),
            location_emoji=data.get("location_emoji", "🏠"),
            location_note=data.get("location_note"),
            task_ids=data.get("task_ids", [])
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WeekSchedule:
    """Estructura de calendario semanal que referencia las entidades de datos."""
    year: int
    month: int
    week_number: int
    weight: Optional[float] = None
    topics_task_ids: List[str] = field(default_factory=list)
    note_ids: List[str] = field(default_factory=list)
    days: List[DaySchedule] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WeekSchedule:
        days_data = [DaySchedule.from_dict(d) for d in data.get("days", [])]
        return cls(
            year=int(data.get("year", 0)),
            month=int(data.get("month", 0)),
            week_number=int(data.get("week_number", 0)),
            weight=data.get("weight"),
            topics_task_ids=data.get("topics_task_ids", []),
            note_ids=data.get("note_ids", []),
            days=days_data
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "year": self.year,
            "month": self.month,
            "week_number": self.week_number,
            "weight": self.weight,
            "topics_task_ids": self.topics_task_ids,
            "note_ids": self.note_ids,
            "days": [d.to_dict() for d in self.days]
        }
