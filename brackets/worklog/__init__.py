"""Módulo worklog: Event Log append-only y log4brackets para registro de actividad."""

from brackets.worklog.event_log import EventLog
from brackets.worklog.log4brackets import log4brackets, Log4Brackets, get_logger

__all__ = ["EventLog", "log4brackets", "Log4Brackets", "get_logger"]
