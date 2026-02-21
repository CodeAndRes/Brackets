#!/usr/bin/env python3
"""
Módulo para análisis y extracción de contenido de archivos de bitácora.
"""

import re
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from brackets.config import (
    TOPICS_SECTION_PATTERN,
    NOTES_SECTION_PATTERN,
    SUBSECTION_PATTERN,
    PENDING_TASK_PATTERN,
    COMPLETED_TASK_PATTERN,
    WEIGHT_PATTERN,
    DATE_SECTION_PATTERN,
    WEEKDAYS,
    MAX_WEEKS_PER_YEAR
)

# Actualizar patrones para nueva estructura
TOPICS_SECTION_PATTERN = r'## ✅Topics\s*(.*?)(?=^##|\Z)'
NOTES_SECTION_PATTERN = r'## 📝Notes\s*(.*?)(?=^##|\Z)'


class ContentParser:
    """Clase para analizar y extraer contenido de archivos de bitácora."""
    
    def __init__(self, content: str):
        self.content = content
    
    def extract_week_info_from_filename(self, filename: str) -> Tuple[Optional[int], Optional[int], Optional[int], Optional[float]]:
        """Extrae información de la semana del nombre del archivo y contenido."""
        # Extraer semana del nombre del archivo
        file_match = re.search(r'\[(\d{4})\]\[(\d{2})\]Week(\d{2})\.md$', filename)
        if not file_match:
            return None, None, None, None
        
        year = int(file_match.group(1))
        month = int(file_match.group(2))
        week_num = int(file_match.group(3))
        
        # Extraer peso del contenido
        weight_match = re.search(WEIGHT_PATTERN, self.content)
        weight = float(weight_match.group(1)) if weight_match else None
        
        return year, month, week_num, weight
    
    def extract_pending_tasks(self) -> List[str]:
        """Extrae todas las tareas pendientes del archivo preservando estructura y jerarquía.
        
        Busca tareas PENDIENTES [ ] en TODO el contenido excepto:
        - Tareas completadas [x]
        - Líneas de metadata (>, ---)
        
        Preserva:
        - Indentación (para relación padre-hijo)
        - Subsecciones (### nivel)
        - Estructura anidada CON SUS PADRES
        
        Importante: Si una subtarea está sin su padre, la función intenta reconstruir la relación.
        """
        pending_tasks = []
        all_lines = []
        
        # Buscar en TOPICS primero (sección principal)
        topics_section = re.search(TOPICS_SECTION_PATTERN, self.content, re.MULTILINE | re.DOTALL)
        if topics_section:
            topics_content = topics_section.group(1)
            lines = topics_content.split('\n')
            
            for line in lines:
                line = line.rstrip()
                
                if line.strip() == '---':
                    break
                
                if not line.strip():
                    continue
                
                # Skip tareas completadas
                if re.match(COMPLETED_TASK_PATTERN, line):
                    continue
                
                # Incluir: tareas pendientes o subsecciones
                if re.match(PENDING_TASK_PATTERN, line) or line.strip().startswith('### '):
                    all_lines.append(line)
        
        # Ahora buscar en TODAS las secciones de días
        # Esto captura tareas pendientes en cualquier día CON SU ESTRUCTURA ANIDADA
        day_sections = re.findall(
            r'##\s+[🏠🚗🏖️](\d+)(.*?)(?=##\s+|\Z)',
            self.content,
            re.MULTILINE | re.DOTALL
        )
        
        for day_num, day_content in day_sections:
            lines = day_content.split('\n')
            
            for line in lines:
                line_stripped = line.rstrip()
                
                if not line_stripped.strip():
                    continue
                
                # Skip completed tasks
                if re.match(COMPLETED_TASK_PATTERN, line_stripped):
                    continue
                
                # Incluir: tareas pendientes o subsecciones (preservando indentación)
                if re.match(PENDING_TASK_PATTERN, line_stripped) or line_stripped.strip().startswith('### '):
                    # Evitar duplicados que ya están en TOPICS
                    clean_line = line_stripped.strip()
                    is_duplicate = any(clean_line == existing.strip() for existing in all_lines)
                    
                    if not is_duplicate:
                        all_lines.append(line_stripped)
        
        # Aplanar pero preservando anidación: convertir 4 espacios = hijo de la anterior
        i = 0
        while i < len(all_lines):
            line = all_lines[i]
            indent = len(line) - len(line.lstrip())
            
            pending_tasks.append(line)
            
            # Si es tarea padre (indent=2), buscar sus hijos (indent=4+)
            if re.match(PENDING_TASK_PATTERN, line) and indent == 2:
                # Buscar líneas siguientes que sean más indentadas (hijos)
                j = i + 1
                while j < len(all_lines):
                    next_line = all_lines[j]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    
                    # Si es hijo (más indentado)
                    if next_indent > indent and (re.match(PENDING_TASK_PATTERN, next_line) or next_line.strip().startswith('### ')):
                        pending_tasks.append(next_line)
                        j += 1
                    # Si volvemos a indent=2, no es hijo
                    elif next_indent <= indent:
                        break
                    else:
                        j += 1
                
                i = j - 1
            
            i += 1
        
        return pending_tasks
    
    def extract_daily_dates(self) -> List[int]:
        """Extrae los números de días de las secciones diarias."""
        dates_found = re.findall(DATE_SECTION_PATTERN, self.content)
        return [int(d) for d in dates_found[:5]]  # Solo los primeros 5 días
    
    def extract_daily_pending_tasks(self) -> List[str]:
        """Extrae las tareas pendientes de los días específicos de la semana."""
        daily_pending = []
        
        # Buscar secciones de días (## 🏠15, ## 🚗16, etc.)
        day_sections = re.findall(r'## [🏠🚗](\d+)\s*(.*?)(?=^##|\Z)', 
                                  self.content, re.MULTILINE | re.DOTALL)
        
        for day_num, day_content in day_sections:
            lines = day_content.split('\n')
            day_tasks = []
            in_previous_tasks = False
            
            for line in lines:
                line = line.strip()
                
                # Detectar si estamos en una sección de tareas anteriores
                if 'Tareas pendientes' in line or 'tareas anteriores' in line.lower():
                    in_previous_tasks = True
                    continue
                
                # Si encontramos ---, salimos de tareas anteriores
                if line == '---':
                    in_previous_tasks = False
                    continue
                
                # Solo extraer tareas que NO están en secciones de tareas anteriores
                if not in_previous_tasks and re.match(r'- \[ \]', line):
                    task_content = re.sub(r'^\s*- \[ \]', '', line).strip()
                    if task_content:  # Solo si la tarea tiene contenido
                        day_tasks.append(f"    - [ ] {task_content}")
            
            # Si este día tenía tareas, agregarlas con referencia al día
            if day_tasks:
                daily_pending.append(f"  - **Día {day_num}:**")
                daily_pending.extend(day_tasks)
        
        return daily_pending
    
    def get_next_week_dates(self) -> List[datetime]:
        """Calcula las fechas de la próxima semana basándose en las fechas actuales del archivo."""
        current_days = self.extract_daily_dates()
        
        if not current_days or len(current_days) < 5:
            return self._get_default_next_week_dates()
        
        # Estrategia mejorada: buscar el mes correcto comparando con la fecha actual
        today = datetime.now()
        
        # Intentar construir las fechas en diferentes meses para encontrar el correcto
        possible_dates = []
        
        # Probar mes actual
        possible_dates.append(self._try_build_dates(current_days, today.year, today.month))
        
        # Probar mes anterior
        prev_month = today.month - 1 if today.month > 1 else 12
        prev_year = today.year if today.month > 1 else today.year - 1
        possible_dates.append(self._try_build_dates(current_days, prev_year, prev_month))
        
        # Probar mes siguiente
        next_month = today.month + 1 if today.month < 12 else 1
        next_year = today.year if today.month < 12 else today.year + 1
        possible_dates.append(self._try_build_dates(current_days, next_year, next_month))
        
        # Filtrar las opciones válidas y elegir la más cercana pero anterior a hoy
        valid_dates = [d for d in possible_dates if d is not None]
        
        if not valid_dates:
            return self._get_default_next_week_dates()
        
        # Elegir las fechas que sean más cercanas y anteriores o iguales a hoy
        best_dates = None
        min_diff = float('inf')
        
        for dates in valid_dates:
            first_date = dates[0]
            # Queremos fechas que sean del pasado o de esta semana
            if first_date <= today:
                diff = (today - first_date).days
                if diff < min_diff:
                    min_diff = diff
                    best_dates = dates
        
        if best_dates is None:
            # Si ninguna es del pasado, tomar la más antigua
            best_dates = min(valid_dates, key=lambda d: d[0])
        
        # Sumar 7 días a las fechas encontradas
        next_week_dates = [date + timedelta(days=7) for date in best_dates]
        return next_week_dates

    def _try_build_dates(self, days: List[int], year: int, month: int) -> Optional[List[datetime]]:
        """Intenta construir fechas para un año y mes específicos."""
        try:
            dates = []
            for day in days:
                dates.append(datetime(year, month, day))
            return dates
        except ValueError:
            # Fecha inválida (ej: 31 de febrero)
            return None
    
    def _adjust_year_month(self, first_day: int, today: datetime) -> Tuple[int, int]:
        """Ajusta el año y mes basándose en el primer día encontrado en el archivo."""
        current_year = today.year
        current_month = today.month
        
        # Calcular la diferencia entre el día del archivo y el día actual
        day_diff = abs(today.day - first_day)
        
        # Si el primer día es mayor que 20 y el día actual es menor (cruce de mes hacia atrás)
        if first_day > 20 and today.day < 15 and day_diff > 15:
            # Las fechas del archivo son del mes anterior
            if current_month == 1:
                current_month = 12
                current_year -= 1
            else:
                current_month -= 1
        
        # Si el primer día es menor que 10 y el día actual es mayor (cruce de mes hacia adelante)
        elif first_day < 10 and today.day > 15 and day_diff > 15:
            # Las fechas del archivo son del mes siguiente
            if current_month == 12:
                current_month = 1
                current_year += 1
            else:
                current_month += 1
        
        # CASO ESPECIAL: Si estamos en los últimos días del mes y el primer día del archivo también
        elif first_day > 20 and today.day > 20:
            # Ambos están en el mismo mes, usar el mes actual
            pass
        
        return current_year, current_month
    
    def _get_default_next_week_dates(self) -> List[datetime]:
        """Obtiene fechas por defecto para la próxima semana basándose en la fecha actual."""
        today = datetime.now()
        
        # Encontrar el lunes de la PRÓXIMA semana
        # No importa qué día sea hoy, buscamos el próximo lunes
        days_since_monday = today.weekday()
        
        # Si hoy es lunes (0), el próximo lunes es en 7 días
        # Si hoy es martes (1), el próximo lunes es en 6 días
        # etc.
        if days_since_monday == 0:
            # Si hoy es lunes, el próximo lunes es en 7 días
            next_monday = today + timedelta(days=7)
        else:
            # Calcular días hasta el próximo lunes
            days_until_next_monday = 7 - days_since_monday
            next_monday = today + timedelta(days=days_until_next_monday)
        
        return [next_monday + timedelta(days=i) for i in range(5)]
    
    def clean_completed_tasks(self) -> str:
        """Remueve las tareas completadas [x] y mantiene las pendientes [ ]."""
        lines = self.content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Si es una tarea completada [x], la omitimos
            if re.match(COMPLETED_TASK_PATTERN, line):
                continue
            # Todas las demás líneas se mantienen
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)


def debug_content_parsing(filepath: str) -> None:
    """Función de debug para analizar el contenido de un archivo."""
    from brackets.utils.legacy_utils import safe_file_read
    
    content = safe_file_read(filepath)
    if not content:
        return
    
    parser = ContentParser(content)
    
    print(f"🔍 DEBUG: Analizando contenido de {filepath}")
    print("=" * 60)
    
    # Información de semana
    year, month, week, weight = parser.extract_week_info_from_filename(filepath)
    print(f"📅 Semana: {week}, Año: {year}, Mes: {month}")
    if weight:
        print(f"⚖️ Peso: {weight}")
    
    # Tareas pendientes
    pending_tasks = parser.extract_pending_tasks()
    print(f"📋 Tareas pendientes encontradas: {len(pending_tasks)}")
    for task in pending_tasks[:3]:  # Mostrar solo las primeras 3
        print(f"  {task}")
    if len(pending_tasks) > 3:
        print(f"  ... y {len(pending_tasks) - 3} más")
    
    # Fechas diarias
    daily_dates = parser.extract_daily_dates()
    print(f"📅 Fechas diarias: {daily_dates}")
    
    # Próximas fechas
    next_dates = parser.get_next_week_dates()
    print(f"🔮 Próximas fechas calculadas:")
    for i, date in enumerate(next_dates):
        print(f"  {WEEKDAYS[i]}: {date.strftime('%d/%m/%Y')}")
    
    # Tareas diarias pendientes
    daily_tasks = parser.extract_daily_pending_tasks()
    print(f"📅 Tareas diarias pendientes: {len(daily_tasks)}")