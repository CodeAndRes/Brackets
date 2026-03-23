#!/usr/bin/env python3
"""
Generador especializado para bitácoras semanales.
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional

from brackets.config import MESSAGES
from brackets.utils.file_finder import FileFinder
from brackets.utils.content_parser import ContentParser
from brackets.utils.content_generator import ContentGenerator
from brackets.utils.legacy_utils import (
    safe_file_read, safe_file_write, confirm_overwrite, 
    parse_float_input, calculate_next_week_info_from_dates, 
    generate_filename, print_calculated_dates
)
from brackets.config import WORKING_DIRECTORY
from brackets.managers.settings_manager import get_global_settings_manager


class WeeklyGenerator:
    """Clase para generar bitácoras semanales."""
    
    def __init__(self, directory: str = ".", settings=None):
        self.directory = directory
        self.settings = settings or get_global_settings_manager(directory)
        self.finder = FileFinder(directory)
        self.generator = ContentGenerator(self.settings)
    
    def create_next_weekly_bitacora(self, ask_for_weight: bool = True) -> bool:
        """Crea la siguiente bitácora semanal basada en la más reciente."""
        
        # Encontrar archivo más reciente
        recent_file = self.finder.get_most_recent_weekly()
        if not recent_file:
            print(MESSAGES['no_files'])
            return False
        
        print(f"📄 Archivo más reciente encontrado: {os.path.basename(recent_file)}")
        
        # Leer contenido
        content = safe_file_read(recent_file)
        if not content:
            return False
        
        # Analizar contenido
        parser = ContentParser(content)
        year, month, current_week, current_weight = parser.extract_week_info_from_filename(recent_file)
        
        if not current_week:
            print("❌ No se pudo extraer la información de la semana del archivo")
            return False
        
        # Mostrar información actual
        self._print_current_info(recent_file, year, month, current_week, current_weight)
        
        # Extraer tareas pendientes (ahora incluye todas las secciones con jerarquía)
        pending_tasks = parser.extract_pending_tasks()
        
        print(f"📋 Tareas pendientes encontradas: {len(pending_tasks)}")
        
        # Pedir peso si es necesario
        new_weight = None
        if ask_for_weight:
            weight_input = input(f"⚖️ Ingresa tu peso para la semana siguiente (Enter para omitir): ").strip()
            new_weight = parse_float_input(weight_input)
        # Calcular fechas PRIMERO
        try:
            next_week_dates = self._calculate_next_week_dates_iso(year, current_week)
            print_calculated_dates(0, next_week_dates)  # Mostrar sin número de semana aún
        except Exception as iso_error:
            # Fallback al parser legacy para no romper flujos existentes.
            try:
                print(f"⚠️ Cálculo ISO no disponible ({iso_error}). Usando fallback legacy...")
                next_week_dates = parser.get_next_week_dates()
                print_calculated_dates(0, next_week_dates)
            except Exception as e:
                print(f"⚠️ Error calculando fechas: {e}")
                return False
        
        # Calcular próxima semana basándose en las fechas reales
        next_year, next_month, next_week = calculate_next_week_info_from_dates(next_week_dates, current_week)
        
        print(f"📅 Nueva semana calculada: Semana {next_week}, {next_month:02d}/{next_year}")
        
        # Generar contenido
        new_content = self.generator.create_weekly_bitacora(
            pending_tasks=pending_tasks,
            week_num=next_week,
            weight=new_weight,
            dates=next_week_dates
        )
        
        # Crear archivo
        new_filename = generate_filename(next_year, next_month, next_week)
        
        if not confirm_overwrite(new_filename):
            print(MESSAGES['operation_cancelled'])
            return False
        
        if safe_file_write(new_filename, new_content):
            print(MESSAGES['file_created'].format(filename=new_filename))
            
            # Mostrar resumen
            summary = self.generator.create_week_summary(
                week_num=next_week,
                dates=next_week_dates,
                pending_count=len(pending_tasks),
                weight=new_weight
            )
            print(summary)
            return True
        
        return False
    
    def _print_current_info(self, filepath: str, year: int, month: int, week: int, weight: Optional[float]):
        """Imprime información del archivo actual."""
        print(f"📅 Archivo: {os.path.basename(filepath)}")
        print(f"📅 Semana actual: {week}, Año: {year}, Mes: {month}")
        if weight:
            print(f"⚖️ Peso actual registrado: {weight}")

    def _calculate_next_week_dates_iso(self, year: int, week: int) -> List[datetime]:
        """Calcula lunes-viernes de la siguiente semana usando calendario ISO.

        Esta ruta evita depender de encabezados diarios parseados del archivo,
        que pueden variar por emojis/ediciones manuales y provocar saltos de día.
        """
        if not year or not week:
            raise ValueError("Año/semana ISO inválidos")

        current_monday = datetime.fromisocalendar(year, week, 1)
        next_monday = current_monday + timedelta(days=7)
        return [next_monday + timedelta(days=i) for i in range(5)]
    
    def create_weekly_from_template(self, week_num: int, year: int, month: int) -> bool:
        """Crea una bitácora semanal desde una plantilla."""
        from datetime import datetime, timedelta
        # TODO: TemplateGenerator no existe aún en content_generator
        # from brackets.utils.content_generator import TemplateGenerator
        
        # Calcular fechas para la semana especificada
        # Esto es simplificado - en una implementación real necesitarías
        # un cálculo más preciso basado en el número de semana
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        dates = [monday + timedelta(days=i) for i in range(5)]
        
        # Generar plantilla
        content = TemplateGenerator.create_empty_weekly_template(week_num, dates)
        
        # Crear archivo
        filename = generate_filename(year, month, week_num)
        
        if not confirm_overwrite(filename):
            print(MESSAGES['operation_cancelled'])
            return False
        
        if safe_file_write(filename, content):
            print(MESSAGES['file_created'].format(filename=filename))
            return True
        
        return False
    
    def create_manual_weekly_bitacora(self) -> bool:
        """Crea una bitácora semanal de forma manual sin necesidad de archivo previo."""
        from datetime import datetime
        
        print("\n📝 CREAR BITÁCORA SEMANAL MANUAL")
        print("=" * 40)
        
        # Pedir año
        year_input = input("📅 Año (Enter para actual): ").strip()
        year = int(year_input) if year_input else datetime.now().year
        
        # Pedir mes
        while True:
            month_input = input("📅 Mes (1-12): ").strip()
            try:
                month = int(month_input)
                if 1 <= month <= 12:
                    break
                print("❌ Mes debe estar entre 1 y 12")
            except ValueError:
                print("❌ Ingresa un número válido")
        
        # Pedir número de semana
        while True:
            week_input = input("📅 Número de semana (1-53): ").strip()
            try:
                week = int(week_input)
                if 1 <= week <= 53:
                    break
                print("❌ Semana debe estar entre 1 y 53")
            except ValueError:
                print("❌ Ingresa un número válido")
        
        # Pedir peso (opcional)
        weight_input = input("⚖️ Peso inicial (Enter para omitir): ").strip()
        weight = parse_float_input(weight_input) if weight_input else None
        
        # Generar nombre de archivo
        filename = generate_filename(
            year=year,
            month=month,
            week=week,
            directory=self.directory
        )
        
        # Pedir ubicaciones de trabajo para cada día
        print("\n🏠 PATRONES DE TRABAJO")
        print("Ingresa la ubicación para cada día:")
        print("  1 = 🏠 Casa")
        print("  2 = 🚗 Oficina")
        print("  3 = 🏖️ Vacaciones/Festivo")
        print("-" * 40)
        
        work_locations = {}
        weekdays = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        day_emoji_map = {0: 29, 1: 30, 2: 31, 3: 1, 4: 2}  # Números de día genéricos
        
        for i, day in enumerate(weekdays):
            while True:
                location = input(f"{day} ({day_emoji_map[i]}): (1/2/3 o emoji): ").strip()
                choice_map = {
                    '1': '🏠',
                    '2': '🚗',
                    '3': '🏖️',
                    '🏠': '🏠',
                    '🚗': '🚗',
                    '🏖️': '🏖️',
                }
                if location in choice_map:
                    work_locations[day_emoji_map[i]] = choice_map[location]
                    break
                print("❌ Ingresa 1/2/3 o 🏠/🚗/🏖️")
        
        # Generar contenido
        content = self.generator.generate_weekly_content_manual(
            year=year,
            month=month,
            week=week,
            weight=weight,
            work_locations=work_locations
        )
        
        if not content:
            print("❌ Error generando contenido")
            return False
        
        print(f"\n📄 Archivo a crear: {os.path.basename(filename)}")
        print(f"📊 Año: {year}, Mes: {month:02d}, Semana: {week}")
        
        # Confirmar sobrescritura si existe
        if os.path.exists(filename):
            if not confirm_overwrite(os.path.basename(filename)):
                print(MESSAGES['operation_cancelled'])
                return False
        
        # Guardar archivo
        if safe_file_write(filename, content):
            print(f"\n✅ {MESSAGES['file_created'].format(filename=os.path.basename(filename))}")
            return True
        
        return False
    
    def list_recent_weeks(self, count: int = 5) -> None:
        """Lista las últimas bitácoras semanales."""
        weekly_files = self.finder.list_weekly_files()
        
        if not weekly_files:
            print("📅 No se encontraron bitácoras semanales")
            return
        
        print(f"📅 Últimas {min(count, len(weekly_files))} bitácoras semanales:")
        for filepath, year, month, week in weekly_files[-count:]:
            filename = os.path.basename(filepath)
            print(f"  {filename} -> Semana {week}, {month:02d}/{year}")


def create_weekly_interactive() -> bool:
    """Función interactiva para crear bitácora semanal."""
    generator = WeeklyGenerator()
    
    print("🗓️ Generador de Bitácora Semanal")
    print("=" * 40)
    
    return generator.create_next_weekly_bitacora()


if __name__ == "__main__":
    create_weekly_interactive()
