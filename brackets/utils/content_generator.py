#!/usr/bin/env python3
"""
Módulo para generar contenido de archivos de bitácora.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from brackets.config import WEEKDAYS
from brackets.utils.legacy_utils import get_season_emoji
from brackets.managers.settings_manager import get_global_settings_manager


class ContentGenerator:
    """Clase para generar contenido de archivos de bitácora."""

    def __init__(self, settings_manager=None):
        self.settings = settings_manager or get_global_settings_manager()
    
    def create_weekly_bitacora(self, 
                             pending_tasks: List[str], 
                             week_num: int, 
                             weight: Optional[float], 
                             dates: List[datetime], 
                             daily_tasks: Optional[List[str]] = None) -> str:
        """Crea el contenido de una nueva bitácora semanal."""
        
        # Encabezado con peso
        weight_str = f" {weight}" if weight else ""
        content = f"# 🗓️Week {week_num}{weight_str}\n\n"
        
        # Sección de topics con tareas pendientes (preserva jerarquía)
        content += "## ✅Topics\n"
        if pending_tasks:
            for task in pending_tasks:
                content += f"{task}\n"
        else:
            content += "  - [ ] \n"
        
        content += "  ---\n"
        
        # Sección de notas
        content += "\n## 📝Notes\n"
        content += "  - \n"
        content += "  ---\n"
        
        # Sección de días de la semana (sin tareas de días anteriores)
        content += "\n"
        
        for i, date in enumerate(dates):
            day_num = date.day
            location, note = self.settings.get_location_for_date(date, week_num)
            header = f"## {location}{day_num}"
            if note:
                header += f" ({note})"
            
            content += f"{header}\n"
            content += "  - \n\n"
        
        return content
    
    def generate_weekly_content_manual(self,
                                      year: int,
                                      month: int, 
                                      week: int,
                                      weight: Optional[float] = None,
                                      work_locations: Optional[dict] = None) -> str:
        """Genera contenido de bitácora semanal de forma manual sin archivo previo."""
        
        # Calcular fechas de la semana ISO
        try:
            # Buscar el lunes de la semana ISO especificada
            jan_4 = datetime(year, 1, 4)
            # El lunes de la semana 1 es el lunes de la semana que contiene el 4 de enero
            week_1_monday = jan_4 - timedelta(days=jan_4.weekday())
            target_monday = week_1_monday + timedelta(weeks=week - 1)
            
            # Generar fechas de lunes a viernes
            dates = [target_monday + timedelta(days=i) for i in range(5)]
        except Exception as e:
            print(f"❌ Error calculando fechas: {e}")
            return None
        
        # Encabezado con peso
        weight_str = f" {weight}" if weight else ""
        content = f"# 🗓️Week {week}{weight_str}\n\n"
        
        # Sección de topics vacía
        content += "## ✅Topics\n"
        content += "  - [ ] \n"
        content += "  ---\n\n"
        
        # Sección de notas
        content += "## 📝Notes\n"
        content += "  - \n"
        content += "  ---\n\n"
        
        # Usar work_locations si se proporciona, sino usar la función por defecto
        for i, date in enumerate(dates):
            day_num = date.day
            
            # Determinar ubicación
            note = None
            if work_locations and day_num in work_locations:
                location = work_locations[day_num]
            else:
                location, note = self.settings.get_location_for_date(date, week)
            
            header = f"## {location}{day_num}"
            if note:
                header += f" ({note})"
            content += f"{header}\n"
            content += "  - \n\n"
        
        return content
    
    def create_monthly_topics(self, 
                            month: int, 
                            year: int, 
                            base_content: str) -> str:
        """Crea el contenido de un archivo mensual de topics."""
        
        # Limpiar tareas completadas del contenido base
        cleaned_content = self._clean_completed_tasks(base_content)
        
        # Agregar emoji de estación al título
        season_emoji = get_season_emoji(month)
        
        if not cleaned_content.startswith('#'):
            cleaned_content = f"# {season_emoji} Topics - Mes {month:02d}\n\n" + cleaned_content
        else:
            # Reemplazar el título existente
            lines = cleaned_content.split('\n')
            lines[0] = f"# {season_emoji} Topics - Mes {month:02d}"
            cleaned_content = '\n'.join(lines)
        
        return cleaned_content
    
    def _clean_completed_tasks(self, content: str) -> str:
        """Remueve las tareas completadas [x] y mantiene las pendientes [ ]."""
        import re
        from brackets.config import COMPLETED_TASK_PATTERN
        
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Si es una tarea completada [x], la omitimos
            if re.match(COMPLETED_TASK_PATTERN, line):
                continue
            # Todas las demás líneas se mantienen
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def create_week_summary(self, 
                          week_num: int, 
                          dates: List[datetime], 
                          pending_count: int, 
                          weight: Optional[float] = None) -> str:
        """Crea un resumen de la semana creada."""
        
        summary = []
        summary.append(f"📅 Semana {week_num}")
        
        if weight:
            summary.append(f"⚖️ Peso registrado: {weight}")
        
        # Patrón de trabajo
        summary.append(f"🏢 Patrón de trabajo para semana {week_num}:")
        for i, date in enumerate(dates):
            location, note = self.settings.get_location_for_date(date, week_num)
            label = self._location_label_from_emoji(location)
            suffix = f" ({note})" if note else ""
            summary.append(f"  {WEEKDAYS[i]} {date.day}: {location} {label}{suffix}")
        
        # Información de tareas
        if pending_count > 0:
            summary.append(f"📋 Se transfirieron {pending_count} tareas pendientes")
        else:
            summary.append("📋 No hay tareas pendientes para transferir")
        
        return '\n'.join(summary)
    
    def create_monthly_summary(self, 
                             month: int, 
                             year: int, 
                             filename: str) -> str:
        """Crea un resumen del archivo mensual creado."""
        
        season_emoji = get_season_emoji(month)
        
        summary = []
        summary.append(f"📅 Mes: {month:02d}/{year}")
        summary.append(f"{season_emoji} Estación aplicada")
        summary.append(f"📄 Archivo: {filename}")
        
        return '\n'.join(summary)

    def _location_label_from_emoji(self, emoji: str) -> str:
        reverse = {v: k for k, v in self.settings.data.get("locations", {}).items()}
        key = reverse.get(emoji)
        labels = {
            "home": "Casa",
            "office": "Oficina",
            "remote": "Remoto",
            "off": "Libre",
        }
        return labels.get(key, "Ubicación")


class TemplateGenerator:
    """Clase para generar plantillas y contenido predeterminado."""
    
    @staticmethod
    def create_empty_weekly_template(week_num: int, dates: List[datetime]) -> str:
        """Crea una plantilla vacía para una bitácora semanal."""
        generator = ContentGenerator()
        return generator.create_weekly_bitacora(
            pending_tasks=[],
            week_num=week_num,
            weight=None,
            dates=dates,
            daily_tasks=None
        )
    
    @staticmethod
    def create_empty_monthly_template(month: int, year: int) -> str:
        """Crea una plantilla vacía para un archivo mensual."""
        season_emoji = get_season_emoji(month)
        
        template = f"""# {season_emoji} Topics - Mes {month:02d}

## 🎯 Objetivos del Mes
  - [ ] 

## 📋 Proyectos Principales
  - [ ] 

## 🔄 Tareas Recurrentes
  - [ ] 

## 💡 Ideas y Notas
  - [ ] 

## 📚 Aprendizaje
  - [ ] 

---

## 📊 Métricas y Seguimiento
  - [ ] 
"""
        return template


def create_content_preview(content: str, max_lines: int = 10) -> str:
    """Crea una vista previa del contenido generado."""
    lines = content.split('\n')
    preview_lines = lines[:max_lines]
    
    preview = '\n'.join(preview_lines)
    
    if len(lines) > max_lines:
        preview += f"\n... ({len(lines) - max_lines} líneas más)"
    
    return preview
