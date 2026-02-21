"""
Sistema Brackets - Generador de Bitácoras y Gestión de Proyectos
Version 2.0 - Arquitectura Refactorizada
"""

__version__ = "2.0.0"
__author__ = "Usuario"

# Exponer clases principales para importación fácil
from brackets.consolidators.month import MonthConsolidator
from brackets.consolidators.year import YearConsolidator

__all__ = [
    "MonthConsolidator",
    "YearConsolidator",
]
