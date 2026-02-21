#!/usr/bin/env python3
"""
Consolidador de archivos de un mes específico.
Refactorizado para usar BaseConsolidator y configuración centralizada.
"""

import os
import re
from typing import List, Tuple, Optional
from datetime import datetime

# Importaciones de nueva arquitectura
from brackets.core.base_consolidator import BaseConsolidator
from brackets.utils.file_finder import FileFinder
from brackets.utils.legacy_utils import safe_file_read, safe_file_write
from brackets.config import MONTH_NAMES, SEASON_EMOJIS, WORKING_DIRECTORY


class MonthConsolidator(BaseConsolidator):
    """Consolidador de archivos de un mes específico."""
    
    def __init__(self, directory: str = "."):
        super().__init__(directory)
        self.finder = FileFinder(directory)
    
    def get_season_emoji(self, month: int) -> str:
        """Obtiene el emoji de la estación según el mes."""
        for months, emoji in SEASON_EMOJIS.items():
            if month in months:
                return emoji
        return "📅"
    
    def get_files_for_month(self, year: int, month: int) -> Tuple[List[str], Optional[str], Optional[str]]:
        """
        Obtiene todos los archivos de un mes específico.
        Retorna: (weekly_files, monthly_topics_file, year_topics_file)
        """
        # Buscar archivos semanales
        weekly_files = []
        
        for file in os.listdir(self.directory):
            if re.match(rf'\[{year}\]\[{month:02d}\]Week\d{{2}}\.md', file):
                filepath = os.path.join(self.directory, file)
                # Extraer número de semana para ordenar
                match = re.search(r'Week(\d{2})', file)
                if match:
                    week_num = int(match.group(1))
                    weekly_files.append((filepath, week_num))
        
        # Ordenar por número de semana (descendente para orden inverso)
        weekly_files.sort(key=lambda x: x[1], reverse=True)
        weekly_files = [f[0] for f in weekly_files]
        
        # Buscar archivo mensual
        monthly_file = None
        monthly_pattern = f"[{year}][{month:02d}]MonthTopics.md"
        monthly_path = os.path.join(self.directory, monthly_pattern)
        if os.path.exists(monthly_path):
            monthly_file = monthly_path
        
        # Buscar archivo de año
        year_file = None
        year_pattern = f"[{year}][00]YearTopics.md"
        year_path = os.path.join(self.directory, year_pattern)
        if os.path.exists(year_path):
            year_file = year_path
        
        return weekly_files, monthly_file, year_file
    
    def delete_source_files(self, weekly_files: List[str], monthly_file: Optional[str]) -> bool:
        """Borra los archivos origen después de confirmar."""
        files_to_delete = weekly_files.copy()
        if monthly_file:
            files_to_delete.append(monthly_file)
        
        if self.confirm_deletion(files_to_delete, "archivo"):
            self.delete_files_confirmed(files_to_delete)
            return True
        else:
            print("\n↩️  Operación de borrado cancelada")
            return False
    
    def consolidate(self, year: int, month: int) -> bool:
        """
        Consolida todos los archivos de un mes en un único archivo.
        El orden es inverso: semanas de mayor a menor.
        """
        return self.consolidate_month(year, month)
    
    def consolidate_month(self, year: int, month: int) -> bool:
        """
        Consolida todos los archivos de un mes en un único archivo.
        El orden es inverso: semanas de mayor a menor.
        """
        print(f"\n🔍 Buscando archivos para {year}-{month:02d}...")
        
        weekly_files, monthly_file, year_file = self.get_files_for_month(year, month)
        
        if not weekly_files and not monthly_file:
            print(f"❌ No se encontraron archivos para {year}-{month:02d}")
            return False
        
        # Verificar si el consolidado ya existe
        output_filename = f"[{year}][{month:02d}].md"
        output_path = os.path.join(self.directory, output_filename)
        
        if os.path.exists(output_path):
            action = self.handle_existing_output(output_filename)
            
            if action == 'delete_only':
                # Solo borrar archivos origen
                return self.delete_source_files(weekly_files, monthly_file)
            elif action != 'regenerate':
                print("\n↩️  Operación cancelada")
                return False
            # Si es 'regenerate', continúa con la regeneración
        
        print(f"\n📁 Archivos encontrados:")
        if monthly_file:
            print(f"  - Temas mensuales: {os.path.basename(monthly_file)}")
        for wf in weekly_files:
            print(f"  - {os.path.basename(wf)}")
        
        # Crear contenido consolidado
        season_emoji = self.get_season_emoji(month)
        month_name = MONTH_NAMES.get(month, f'Mes {month:02d}')
        
        content_parts = []
        
        # Encabezado principal
        content_parts.append(f"# {season_emoji} {month_name} - {year}")
        content_parts.append("")
        content_parts.append(f"> Consolidado del mes {month:02d}/{year}")
        content_parts.append(f"> Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content_parts.append("")
        content_parts.append("---")
        content_parts.append("")
        
        # Agregar temas mensuales si existe
        if monthly_file:
            content_parts.append("## 📋 Temas Mensuales")
            content_parts.append("")
            monthly_content = safe_file_read(monthly_file)
            if monthly_content:
                # Remover el primer encabezado del archivo
                lines = monthly_content.split('\n')
                content_without_title = '\n'.join(lines[1:]).strip()
                content_parts.append(content_without_title)
                content_parts.append("")
                content_parts.append("---")
                content_parts.append("")
        
        # Agregar semanas (en orden inverso, ya están ordenadas)
        for i, weekly_file in enumerate(weekly_files, 1):
            # Extraer número de semana del nombre del archivo
            match = re.search(r'Week(\d{2})', os.path.basename(weekly_file))
            week_num = match.group(1) if match else "??"
            
            content_parts.append(f"## 🗓️ Semana {week_num}")
            content_parts.append("")
            
            weekly_content = safe_file_read(weekly_file)
            if weekly_content:
                # Usar método de BaseConsolidator para ajustar encabezados
                adjusted_content = self.adjust_markdown_headings(weekly_content, skip_first_line=True)
                content_parts.append(adjusted_content.strip())
                content_parts.append("")
                content_parts.append("---")
                content_parts.append("")
        
        # Escribir archivo consolidado
        final_content = '\n'.join(content_parts)
        
        if safe_file_write(output_path, final_content):
            print(f"\n✅ Archivo consolidado creado: {output_filename}")
            print(f"📍 Ruta: {output_path}")
            
            # Preguntar si borrar archivos origen
            delete = input("\n🗑️  ¿Deseas borrar los archivos origen? (s/N): ").strip().lower()
            
            if delete in ['s', 'si', 'sí', 'y', 'yes']:
                self.delete_source_files(weekly_files, monthly_file)
            
            return True
        else:
            print(f"\n❌ Error al crear el archivo consolidado")
            return False
    
    def list_available_months(self) -> List[Tuple[int, int]]:
        """Lista todos los meses disponibles con archivos."""
        months_set = set()
        
        # Buscar todos los archivos de semanas y meses
        for file in os.listdir(self.directory):
            # Buscar patrón [YYYY][MM]
            match = re.match(r'\[(\d{4})\]\[(\d{2})\](?:Week\d{2}|MonthTopics)\.md', file)
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                if month > 0:  # Excluir el archivo [00]YearTopics
                    months_set.add((year, month))
        
        # Ordenar por año y mes (descendente)
        return sorted(list(months_set), reverse=True)
    
    def interactive_consolidate(self) -> bool:
        """Modo interactivo para consolidar un mes."""
        print("\n📦 CONSOLIDAR ARCHIVOS DE UN MES")
        print("=" * 40)
        
        available_months = self.list_available_months()
        
        if not available_months:
            print("❌ No se encontraron archivos de bitácoras")
            return False
        
        print("\nMeses disponibles:")
        print("-" * 30)
        
        for i, (year, month) in enumerate(available_months, 1):
            month_name = MONTH_NAMES.get(month, f'Mes {month:02d}')
            print(f"{i:2d}. {year}-{month:02d} ({month_name})")
        
        print("\nO ingresa manualmente (formato: YYYY-MM)")
        print("-" * 30)
        
        choice = input("\nSelecciona un mes (número o formato YYYY-MM): ").strip()
        
        year, month = None, None
        
        # Intentar como número de lista
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(available_months):
                year, month = available_months[choice_num - 1]
        except ValueError:
            # Intentar como formato YYYY-MM
            match = re.match(r'(\d{4})-(\d{2})', choice)
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
        
        if year and month and 1 <= month <= 12:
            return self.consolidate_month(year, month)
        else:
            print("❌ Selección inválida")
            return False


def main():
    """Función principal para pruebas."""
    consolidator = MonthConsolidator()
    consolidator.interactive_consolidate()


if __name__ == "__main__":
    main()
