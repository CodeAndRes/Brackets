#!/usr/bin/env python3
"""
Consolidador de año completo.
Refactorizado para usar BaseConsolidator y configuración centralizada.
"""

import os
import re
from typing import List, Optional, Tuple
from datetime import datetime

# Importaciones de nueva arquitectura
from brackets.core.base_consolidator import BaseConsolidator
from brackets.utils.file_finder import FileFinder
from brackets.utils.legacy_utils import safe_file_read, safe_file_write
from brackets.config import MONTH_NAMES, WORKING_DIRECTORY


class YearConsolidator(BaseConsolidator):
    """Consolidador de archivos de un año completo."""
    
    def __init__(self, directory: str = "."):
        super().__init__(directory)
        self.finder = FileFinder(directory)
    
    def get_files_for_year(self, year: int) -> Tuple[List[Tuple[str, int]], Optional[str]]:
        """
        Obtiene todos los archivos consolidados de meses para un año específico.
        Retorna (month_files, year_topics_file) donde:
          - month_files: lista de (filepath, month) ordenados por mes descendente
          - year_topics_file: ruta al archivo [YYYY][00]YearTopics.md o None
        """
        month_files = []
        
        # Buscar archivos consolidados con formato [YYYY][MM].md
        for file in os.listdir(self.directory):
            match = re.match(rf'\[{year}\]\[(\d{{2}})\]\.md', file)
            if match:
                month = int(match.group(1))
                if month > 0 and month <= 12:  # Meses válidos
                    filepath = os.path.join(self.directory, file)
                    month_files.append((filepath, month))
        
        # Ordenar por mes descendente (12 → 1)
        month_files.sort(key=lambda x: x[1], reverse=True)
        
        # Buscar archivo de temas del año
        year_topics_file = None
        year_topics_pattern = f"[{year}][00]YearTopics.md"
        year_topics_path = os.path.join(self.directory, year_topics_pattern)
        if os.path.exists(year_topics_path):
            year_topics_file = year_topics_path
        
        return month_files, year_topics_file
    
    def delete_source_files(self, month_files: List[Tuple[str, int]]) -> bool:
        """Borra los archivos consolidados mensuales después de confirmar."""
        files_to_delete = [filepath for filepath, _ in month_files]
        
        if self.confirm_deletion(files_to_delete, "archivo(s) consolidado(s) mensual(es)"):
            self.delete_files_confirmed(files_to_delete)
            return True
        else:
            print("\n↩️  Operación de borrado cancelada")
            return False
    
    def consolidate(self, year: int) -> bool:
        """
        Consolida todos los meses de un año en un único archivo.
        El orden es inverso: mes 12 → 01
        """
        return self.consolidate_year(year)
    
    def consolidate_year(self, year: int) -> bool:
        """
        Consolida todos los meses de un año en un único archivo.
        El orden es inverso: mes 12 → 01
        """
        print(f"\n🔍 Buscando archivos consolidados para el año {year}...")
        
        month_files, year_topics_file = self.get_files_for_year(year)
        
        if not month_files:
            print(f"❌ No se encontraron archivos consolidados para el año {year}")
            print(f"   💡 Primero debes crear los consolidados de cada mes con la opción de consolidación mensual")
            return False
        
        # Verificar si el consolidado ya existe
        output_filename = f"[{year}].md"
        output_path = os.path.join(self.directory, output_filename)
        
        if os.path.exists(output_path):
            action = self.handle_existing_output(output_filename)
            
            if action == 'delete_only':
                # Solo borrar archivos origen
                return self.delete_source_files(month_files)
            elif action != 'regenerate':
                print("\n↩️  Operación cancelada")
                return False
            # Si es 'regenerate', continúa con la regeneración
        
        print(f"\n📁 Archivos consolidados encontrados:")
        if year_topics_file:
            print(f"  - Temas del año: {os.path.basename(year_topics_file)}")
        for filepath, month in month_files:
            print(f"  - {os.path.basename(filepath)}")
        
        # Crear contenido consolidado
        content_parts = []
        
        # Encabezado principal
        content_parts.append(f"# 📅 Año {year}")
        content_parts.append("")
        content_parts.append(f"> Consolidado de todo el año {year}")
        content_parts.append(f"> Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content_parts.append("")
        content_parts.append("---")
        content_parts.append("")
        
        # Agregar temas del año si existe
        if year_topics_file:
            content_parts.append("## 📅 Temas del Año")
            content_parts.append("")
            year_content = safe_file_read(year_topics_file)
            if year_content:
                # Remover el primer encabezado del archivo
                lines = year_content.split('\n')
                content_without_title = '\n'.join(lines[1:]).strip()
                content_parts.append(content_without_title)
                content_parts.append("")
                content_parts.append("---")
                content_parts.append("")
        
        # Agregar cada mes (en orden inverso, ya están ordenados)
        for filepath, month in month_files:
            month_name = MONTH_NAMES.get(month, f"Mes {month:02d}")
            
            content_parts.append(f"## 🗓️ {month_name}")
            content_parts.append("")
            
            month_content = safe_file_read(filepath)
            if month_content:
                # Usar método de BaseConsolidator para remover metadata y ajustar
                cleaned_content = self.remove_markdown_metadata(month_content)
                adjusted_content = self.adjust_markdown_headings(
                    cleaned_content, 
                    skip_first_line=False  # Ya quitamos la primera línea con remove_metadata
                )
                
                content_parts.append(adjusted_content.strip())
                content_parts.append("")
                content_parts.append("---")
                content_parts.append("")
        
        # Escribir archivo consolidado
        final_content = '\n'.join(content_parts)
        
        if safe_file_write(output_path, final_content):
            print(f"\n✅ Archivo consolidado del año creado: {output_filename}")
            print(f"📍 Ruta: {output_path}")
            
            # Preguntar si borrar archivos origen (consolidados mensuales)
            delete = input("\n🗑️  ¿Deseas borrar los archivos consolidados mensuales? (s/N): ").strip().lower()
            
            if delete in ['s', 'si', 'sí', 'y', 'yes']:
                self.delete_source_files(month_files)
            
            return True
        else:
            print(f"\n❌ Error al crear el archivo consolidado del año")
            return False
    
    def list_available_years(self) -> List[int]:
        """Lista todos los años disponibles con archivos consolidados."""
        years_set = set()
        
        # Buscar todos los archivos consolidados de meses
        for file in os.listdir(self.directory):
            match = re.match(r'\[(\d{4})\]\[\d{2}\]\.md', file)
            if match:
                year = int(match.group(1))
                years_set.add(year)
        
        # Ordenar descendente
        return sorted(list(years_set), reverse=True)
    
    def interactive_consolidate(self) -> bool:
        """Modo interactivo para consolidar un año."""
        print("\n🗓️ CONSOLIDAR AÑO COMPLETO")
        print("=" * 40)
        
        available_years = self.list_available_years()
        
        if not available_years:
            print("❌ No se encontraron archivos consolidados de meses")
            print("💡 Primero debes crear los consolidados mensuales")
            return False
        
        print("\nAños disponibles:")
        print("-" * 30)
        
        for i, year in enumerate(available_years, 1):
            month_files, _ = self.get_files_for_year(year)
            print(f"{i}. {year} ({len(month_files)} meses)")
        
        print("\nO ingresa el año manualmente (YYYY)")
        print("-" * 30)
        
        choice = input("\nSelecciona un año (número o formato YYYY): ").strip()
        
        year = None
        
        # Intentar como número de lista
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(available_years):
                year = available_years[choice_num - 1]
            else:
                year = choice_num  # Intentar como año directo
        except ValueError:
            pass
        
        if year and year >= 1900 and year <= 2100:
            return self.consolidate_year(year)
        else:
            print("❌ Selección inválida")
            return False


def main():
    """Función principal para pruebas."""
    consolidator = YearConsolidator()
    consolidator.interactive_consolidate()


if __name__ == "__main__":
    main()
