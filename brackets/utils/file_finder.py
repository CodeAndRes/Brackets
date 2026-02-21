#!/usr/bin/env python3
"""
Módulo para búsqueda y gestión de archivos de bitácora.
"""

import os
import re
import glob
from typing import List, Optional, Tuple

from brackets.config import WEEKLY_PATTERN, MONTHLY_PATTERN


class FileFinder:
    """Clase para encontrar y gestionar archivos de bitácora."""
    
    def __init__(self, directory: str = "."):
        self.directory = directory
    
    def _get_files_by_pattern(self, pattern: str) -> List[str]:
        """Busca archivos que coincidan con el patrón dado."""
        # Primero buscar con glob pattern directo
        glob_pattern = os.path.join(self.directory, pattern)
        files = glob.glob(glob_pattern)
        
        if not files:
            # Buscar con patrón más flexible usando regex
            all_files = glob.glob(os.path.join(self.directory, "*.md"))
            files = [f for f in all_files if re.search(pattern + '$', f)]
        
        return files
    
    def _extract_week_info(self, filepath: str) -> Optional[Tuple[str, int, int, int]]:
        """Extrae información de semana del nombre del archivo."""
        match = re.search(r'\[(\d{4})\]\[(\d{2})\]Week(\d{2})\.md$', os.path.basename(filepath))
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            week = int(match.group(3))
            return filepath, year, month, week
        return None
    
    def _extract_month_info(self, filepath: str) -> Optional[Tuple[str, int, int]]:
        """Extrae información de mes del nombre del archivo."""
        match = re.search(r'\[(\d{4})\]\[(\d{2})\]MonthTopics\.md$', os.path.basename(filepath))
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            return filepath, year, month
        return None
    
    def get_most_recent_weekly(self) -> Optional[str]:
        """Encuentra el archivo de bitácora semanal más reciente."""
        files = self._get_files_by_pattern(WEEKLY_PATTERN)
        
        if not files:
            return None
        
        # Extraer información de semana y ordenar
        file_info = []
        for file in files:
            info = self._extract_week_info(file)
            if info:
                file_info.append(info)
        
        if not file_info:
            return None
        
        # Ordenar por año, mes, semana y devolver el más reciente
        file_info.sort(key=lambda x: (x[1], x[2], x[3]))
        return file_info[-1][0]
    
    def get_most_recent_monthly(self) -> Optional[str]:
        """Encuentra el archivo mensual más reciente."""
        files = self._get_files_by_pattern(MONTHLY_PATTERN)
        
        if not files:
            return None
        
        # Extraer información de mes y ordenar
        file_info = []
        for file in files:
            info = self._extract_month_info(file)
            if info:
                file_info.append(info)
        
        if not file_info:
            return None
        
        # Ordenar por año, mes y devolver el más reciente
        file_info.sort(key=lambda x: (x[1], x[2]))
        return file_info[-1][0]
    
    def list_weekly_files(self) -> List[Tuple[str, int, int, int]]:
        """Lista todos los archivos semanales con su información."""
        files = self._get_files_by_pattern(WEEKLY_PATTERN)
        
        file_info = []
        for file in files:
            info = self._extract_week_info(file)
            if info:
                file_info.append(info)
        
        # Ordenar por año, mes, semana
        file_info.sort(key=lambda x: (x[1], x[2], x[3]))
        return file_info
    
    def list_monthly_files(self) -> List[Tuple[str, int, int]]:
        """Lista todos los archivos mensuales con su información."""
        files = self._get_files_by_pattern(MONTHLY_PATTERN)
        
        file_info = []
        for file in files:
            info = self._extract_month_info(file)
            if info:
                file_info.append(info)
        
        # Ordenar por año, mes
        file_info.sort(key=lambda x: (x[1], x[2]))
        return file_info
    
    def find_file_by_week(self, year: int, month: int, week: int) -> Optional[str]:
        """Busca un archivo específico por año, mes y semana."""
        filename = f"[{year:04d}][{month:02d}]Week{week:02d}.md"
        filepath = os.path.join(self.directory, filename)
        
        if os.path.exists(filepath):
            return filepath
        return None
    
    def find_file_by_month(self, year: int, month: int) -> Optional[str]:
        """Busca un archivo específico por año y mes."""
        filename = f"[{year:04d}][{month:02d}]MonthTopics.md"
        filepath = os.path.join(self.directory, filename)
        
        if os.path.exists(filepath):
            return filepath
        return None


def debug_files_in_directory(directory: str = ".") -> None:
    """Función de debug para mostrar información sobre archivos encontrados."""
    finder = FileFinder(directory)
    
    print("🔍 DEBUG: Archivos de bitácora encontrados")
    print("=" * 50)
    
    weekly_files = finder.list_weekly_files()
    print(f"📅 Archivos semanales ({len(weekly_files)}):")
    for filepath, year, month, week in weekly_files:
        print(f"  {os.path.basename(filepath)} -> {year}/{month:02d}/W{week:02d}")
    
    monthly_files = finder.list_monthly_files()
    print(f"\n📋 Archivos mensuales ({len(monthly_files)}):")
    for filepath, year, month in monthly_files:
        print(f"  {os.path.basename(filepath)} -> {year}/{month:02d}")
    
    # Mostrar archivos más recientes
    recent_weekly = finder.get_most_recent_weekly()
    recent_monthly = finder.get_most_recent_monthly()
    
    print(f"\n🎯 Más reciente semanal: {os.path.basename(recent_weekly) if recent_weekly else 'N/A'}")
    print(f"🎯 Más reciente mensual: {os.path.basename(recent_monthly) if recent_monthly else 'N/A'}")
