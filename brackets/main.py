#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal para el generador de bitácoras.
Proporciona un menú interactivo para todas las funciones.
"""

import sys
import os
from typing import Dict, Callable, Optional

# Configurar UTF-8 para Windows
if sys.platform == 'win32':
    import io
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from brackets.generators.weekly import WeeklyGenerator
from brackets.generators.monthly import MonthlyGenerator
from brackets.utils.file_finder import FileFinder, debug_files_in_directory
from brackets.utils.content_parser import debug_content_parsing
from brackets.utils.legacy_utils import test_emoji_pattern
from brackets.managers.settings_manager import SettingsManager, set_global_settings_manager
from brackets.managers.file_rename_manager import FileRenameManager

# Importar consolidadores desde nueva arquitectura
from brackets.consolidators.month import MonthConsolidator
from brackets.consolidators.year import YearConsolidator


def clear_screen():
    """Limpia la pantalla de la consola."""
    os.system('cls' if os.name == 'nt' else 'clear')


class BitacoraManager:
    """Clase principal para gestionar las bitácoras."""

    def __init__(self, directory: str = "."):
        self.vault_root = os.path.abspath(directory)
        self.paths = self._load_vault_paths()
        self.notes_root = self.paths["notes_root"]
        self.data_dir = self.paths["data_dir"]
        self.directory = self.notes_root
        self.feature_flags = self._load_feature_flags()
        self.bitacoras_enabled = bool(self.feature_flags.get("bitacoras_enabled", True))
        self.vault_name = self._get_vault_name()
        self.settings = SettingsManager(directory)
        set_global_settings_manager(self.settings)
        self.weekly_gen = WeeklyGenerator(self.notes_root, self.settings)
        self.monthly_gen = MonthlyGenerator(self.notes_root)
        self.month_consolidator = MonthConsolidator(self.notes_root)
        self.year_consolidator = YearConsolidator(self.notes_root)
        self.finder = FileFinder(self.notes_root)
        self.category_manager = None  # Lazy load cuando se necesite
        self.file_rename_manager = None  # Lazy load cuando se necesite

    def _load_vault_paths(self) -> Dict[str, str]:
        """Carga rutas configurables del vault desde data/config.yaml."""
        notes_root = self.vault_root
        data_dir = os.path.join(self.vault_root, "data")

        config_path = os.path.join(self.vault_root, "data", "config.yaml")
        if not os.path.exists(config_path):
            return {
                "notes_root": notes_root,
                "data_dir": data_dir,
            }

        try:
            import yaml

            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}

            paths = config_data.get("paths", {})
            if isinstance(paths, dict):
                configured_notes = paths.get("notes_root")
                if isinstance(configured_notes, str) and configured_notes.strip():
                    candidate = configured_notes.strip()
                    notes_root = candidate if os.path.isabs(candidate) else os.path.join(self.vault_root, candidate)

                configured_data = paths.get("data_dir")
                if isinstance(configured_data, str) and configured_data.strip():
                    candidate = configured_data.strip()
                    data_dir = candidate if os.path.isabs(candidate) else os.path.join(self.vault_root, candidate)

        except Exception:
            pass

        return {
            "notes_root": os.path.normpath(notes_root),
            "data_dir": os.path.normpath(data_dir),
        }

    def _load_feature_flags(self) -> Dict[str, bool]:
        """Carga feature flags desde data/config.yaml con fallback seguro."""
        config_path = os.path.join(self.vault_root, "data", "config.yaml")
        if not os.path.exists(config_path):
            return {}

        try:
            import yaml

            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}

            flags = config_data.get("feature_flags", {})
            return flags if isinstance(flags, dict) else {}
        except Exception:
            return {}

    def _get_vault_name(self) -> str:
        """Obtiene el nombre del vault desde config.yaml o del nombre del directorio."""
        config_path = os.path.join(self.vault_root, "data", "config.yaml")

        # Intentar leer desde config.yaml
        if os.path.exists(config_path):
            try:
                import yaml
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = yaml.safe_load(f) or {}
                vault_name = config_data.get("vault_name")
                if vault_name and isinstance(vault_name, str):
                    return vault_name.strip()
            except Exception:
                pass

        # Fallback: usar nombre del directorio
        return os.path.basename(self.vault_root)

    def _show_bitacoras_disabled_message(self) -> None:
        print("\n⚠️ Función no disponible: bitácoras desactivadas en data/config.yaml")
        print("   Activa 'feature_flags.bitacoras_enabled: true' para usar esta opción.")
        input("\nPresiona Enter para continuar...")

    def show_main_menu(self) -> None:
        """Muestra el menú principal."""
        clear_screen()
        print(f"\n🗓️ GENERADOR DE BITÁCORAS - SISTEMA BRACKETS")
        print(f"📁 Vault: {self.vault_name}")
        print("=" * 50)
        if self.bitacoras_enabled:
            print("1. 📝 Generación de Bitácoras")
            print("2. 📦 Consolidación de Archivos")
        else:
            print("1. 🚫 Generación de Bitácoras (desactivado)")
            print("2. 🚫 Consolidación de Archivos (desactivado)")
        print("3. 📂 Gestión de Archivos y Categorías")
        print("4. 🔧 Herramientas y Utilidades")
        print("5. ⚙️ Configuración")
        print("6. ❓ Ayuda")
        print("0. 🚪 Salir")
        print("-" * 50)

    def show_generation_menu(self) -> None:
        """Muestra el menú de generación."""
        clear_screen()
        print(f"\n📝 GENERACIÓN DE BITÁCORAS - {self.vault_name}")
        print("=" * 50)
        print("1. 📋 Crear bitácora semanal")
        print("2. ✏️ Crear bitácora semanal manual")
        print("3. 📋 Crear archivo mensual")
        print("0. ↩️ Volver al menú principal")
        print("-" * 40)

    def show_consolidation_menu(self) -> None:
        """Muestra el menú de consolidación."""
        clear_screen()
        print(f"\n📦 CONSOLIDACIÓN DE ARCHIVOS - {self.vault_name}")
        print("=" * 50)
        print("1. 📋 Consolidar mes completo")
        print("2. 📋 Consolidar año completo")
        print("0. ↩️ Volver al menú principal")
        print("-" * 40)

    def show_file_management_menu(self) -> None:
        """Muestra el menú de gestión de archivos."""
        clear_screen()
        print(f"\n📂 GESTIÓN DE ARCHIVOS Y CATEGORÍAS - {self.vault_name}")
        print("=" * 60)
        print("1. 📋 Listar archivos recientes")
        print("2. 📄 Analizar archivo específico")
        print("3. 📚 Gestionar categorías y documentos")
        print("4. 🔍 Búsqueda y reemplazo global")
        print("5. 🔄 Sincronizar YAML con repositorio")
        print("0. ↩️ Volver al menú principal")
        print("-" * 50)

    def show_tools_menu(self) -> None:
        """Muestra el menú de herramientas."""
        clear_screen()
        print(f"\n🔧 HERRAMIENTAS Y UTILIDADES - {self.vault_name}")
        print("=" * 50)
        print("1. 🔍 Analizar contenido de archivo")
        print("2. 📁 Debug archivos en directorio")
        print("3. 🌨 Probar patrón de emojis")
        print("4. 📋 Calcular fechas de archivo")
        print("5. ⏲️ Pomodoro Timer")
        print("0. ↩️ Volver al menú principal")
        print("-" * 40)

    def show_list_menu(self) -> None:
        """Muestra el menú de listado."""
        clear_screen()
        print(f"\n📋 LISTAR ARCHIVOS - {self.vault_name}")
        print("=" * 40)
        print("1. 📝 Bitácoras semanales")
        print("2. 📋 Archivos mensuales")
        print("3. 🔍 Debug - Todos los archivos")
        print("0. ↩️ Volver")
        print("-" * 25)

    def handle_generation_menu(self) -> None:
        """Maneja el submenú de generación."""
        if not self.bitacoras_enabled:
            self._show_bitacoras_disabled_message()
            return

        while True:
            self.show_generation_menu()
            choice = input("Selecciona una opción: ").strip()

            if choice == "1":
                clear_screen()
                self.handle_weekly_creation()
            elif choice == "2":
                clear_screen()
                self.handle_manual_weekly_creation()
            elif choice == "3":
                clear_screen()
                self.handle_monthly_creation()
            elif choice == "0":
                break
            else:
                print("❌ Opción inválida")
                input("\nPresiona Enter para continuar...")

    def handle_consolidation_menu(self) -> None:
        """Maneja el submenú de consolidación."""
        if not self.bitacoras_enabled:
            self._show_bitacoras_disabled_message()
            return

        while True:
            self.show_consolidation_menu()
            choice = input("Selecciona una opción: ").strip()

            if choice == "1":
                clear_screen()
                self.handle_month_consolidation()
            elif choice == "2":
                clear_screen()
                self.handle_year_consolidation()
            elif choice == "0":
                break
            else:
                print("❌ Opción inválida")
                input("\nPresiona Enter para continuar...")

    def handle_file_management_menu(self) -> None:
        """Maneja el submenú de gestión de archivos."""
        while True:
            self.show_file_management_menu()
            choice = input("Selecciona una opción: ").strip()

            if choice == "1":
                clear_screen()
                self.handle_list_files()
            elif choice == "2":
                clear_screen()
                self.handle_analyze_file()
            elif choice == "3":
                clear_screen()
                self.handle_category_management()
            elif choice == "4":
                clear_screen()
                self.handle_file_rename()
            elif choice == "5":
                clear_screen()
                self.handle_sync_yaml()
            elif choice == "0":
                break
            else:
                print("❌ Opción inválida")
                input("\nPresiona Enter para continuar...")

    def handle_tools_menu(self) -> None:
        """Maneja el submenú de herramientas."""
        while True:
            self.show_tools_menu()
            choice = input("Selecciona una opción: ").strip()

            if choice == "1":
                clear_screen()
                filename = input("Nombre del archivo a analizar: ").strip()
                filepath = filename if os.path.exists(filename) else os.path.join(self.directory, filename)
                if os.path.exists(filepath):
                    debug_content_parsing(filepath)
                else:
                    print("❌ Archivo no encontrado")
                input("\nPresiona Enter para continuar...")

            elif choice == "2":
                clear_screen()
                debug_files_in_directory(self.directory)
                input("\nPresiona Enter para continuar...")

            elif choice == "3":
                clear_screen()
                test_emoji_pattern()
                input("\nPresiona Enter para continuar...")

            elif choice == "4":
                clear_screen()
                filename = input("Nombre del archivo para calcular fechas: ").strip()
                from brackets.utils.legacy_utils import safe_file_read
                from brackets.utils.content_parser import ContentParser

                filepath = filename if os.path.exists(filename) else os.path.join(self.directory, filename)
                if os.path.exists(filepath):
                    content = safe_file_read(filepath)
                    if content:
                        parser = ContentParser(content)
                        dates = parser.get_next_week_dates()
                        print("📋 Próximas fechas calculadas:")
                        from brackets.config import WEEKDAYS
                        for i, date in enumerate(dates):
                            print(f"  {WEEKDAYS[i]}: {date.strftime('%d/%m/%Y')}")
                else:
                    print("❌ Archivo no encontrado")
                input("\nPresiona Enter para continuar...")

            elif choice == "5":
                clear_screen()
                from brackets.modules.pomodoro_timer import run_pomodoro_standalone
                run_pomodoro_standalone(self.vault_root)

            elif choice == "0":
                break

            else:
                print("❌ Opción inválida")
                input("\nPresiona Enter para continuar...")

    def handle_sync_yaml(self) -> None:
        """Maneja la sincronización del YAML con el repositorio."""
        print("\n🔄 SINCRONIZAR YAML CON REPOSITORIO")
        print("=" * 50)

        try:
            # Importar las funciones necesarias
            import shutil
            from pathlib import Path

            from brackets.tools.sync_yaml_with_repo import (
                parse_file_structure,
                build_categories_from_repo,
                from_yaml_file,
                merge_categories,
                to_yaml_string,
                get_sync_scan_config,
                check_nomenclature_issues,
                handle_nomenclature_issues,
                apply_name_mappings,
                get_empty_descriptions,
                add_descriptions_to_yaml,
                compare_structures
            )

            # 1. Cargar YAML existente
            yaml_path = os.path.join(self.data_dir, "categories.yaml")
            try:
                existing_categories = from_yaml_file(yaml_path)
                print("  ✓ YAML cargado")
            except FileNotFoundError:
                print(f"  ⚠ No se encontró {yaml_path}, creando desde cero...")
                from brackets.models.yaml_models import CategoriesYAML
                existing_categories = CategoriesYAML(version="1.0.0")

            # 2. Escanear repositorio
            print("  ⏳ Escaneando repositorio...")
            scan_config = get_sync_scan_config(self.vault_root)
            structure = parse_file_structure(
                base_dir=self.notes_root,
                include_extensions=scan_config.get("include_extensions", (".md", ".sql")),
                excluded_prefixes=scan_config.get("excluded_prefixes", ("[2025]", "[2026]", "[🖼️ASSETS]", "[.crossnote]"))
            )
            repo_categories = build_categories_from_repo(structure)
            print("  ✓ Repositorio escaneado")

            # 3. Verificar nomenclatura
            print("  ⏳ Verificando nomenclatura...")
            nomenclature_issues = check_nomenclature_issues(repo_categories)

            if nomenclature_issues:
                print()
                name_mapping = handle_nomenclature_issues(nomenclature_issues)

                if name_mapping is None:
                    print("\n❌ Sincronización cancelada por el usuario")
                    input("\nPresiona Enter para continuar...")
                    return

                if name_mapping:
                    apply_name_mappings(repo_categories, name_mapping)
                    apply_name_mappings(existing_categories, name_mapping)
                    print("  ✓ Nombres aplicados")
            else:
                print("  ✓ Nomenclatura OK")

            # 4. Comparar y fusionar
            print("  ⏳ Comparando estructuras...")
            compare_structures(existing_categories, repo_categories)

            print("  ⏳ Haciendo merge...")
            merged_categories = merge_categories(existing_categories, repo_categories)

            # Detectar descripciones vacías DESPUÉS del merge
            empty_descs = get_empty_descriptions(merged_categories)
            if empty_descs:
                print(f"\n  ⚠ {len(empty_descs)} elementos sin descripción")
                for item in empty_descs[:5]:  # Mostrar primeros 5
                    print(f"    • {item['path']}")
                if len(empty_descs) > 5:
                    print(f"    ... y {len(empty_descs) - 5} más")

                # Permitir al usuario añadir descripciones
                print()
                add_descriptions_to_yaml(merged_categories, empty_descs)

            # 5. Generar YAML
            print("\n  ⏳ Generando YAML...")
            yaml_content = to_yaml_string(merged_categories, indent=2, include_metadata=True)

            output_file = scan_config.get("output_file", "categories_SYNCED.yaml")
            output_path = output_file if os.path.isabs(output_file) else os.path.join(self.vault_root, output_file)
            output_path = os.path.normpath(output_path)

            # Comparar con el original para detectar cambios
            has_changes = True
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    original_content = f.read()
                has_changes = yaml_content.strip() != original_content.strip()
            except FileNotFoundError:
                has_changes = True  # Si no existe, es un "cambio"

            if not has_changes:
                # Sin cambios - no hay nada que hacer
                print("  ✓ Sin cambios - nada que sincronizar")
                # Borrar archivo temporal si existe
                if os.path.exists(output_path):
                    os.remove(output_path)
            else:
                # Hay cambios - guardar y preguntar
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(yaml_content)

                print(f"  ✓ Archivo temporal creado: {output_path}")

                # 6. Preguntar si reemplazar el archivo definitivo
                print("\n¿Reemplazar 'data/categories.yaml' con la versión sincronizada? (s/n): ", end="")
                while True:
                    choice = input().strip().lower()
                    if choice in ['s', 'n', 'si', 'no']:
                        break
                    print("Por favor, ingresa 's' o 'n': ", end="")

                if choice in ['s', 'si']:
                    # Crear respaldo
                    backup_path = yaml_path + ".backup"
                    if os.path.exists(yaml_path):
                        shutil.copy2(yaml_path, backup_path)
                        print(f"  ✓ Respaldo creado: {backup_path}")

                    # Reemplazar
                    shutil.copy(output_path, yaml_path)
                    print("  ✓ 'data/categories.yaml' actualizado")
                    # Borrar archivo temporal
                    os.remove(output_path)
                else:
                    print(f"  ℹ Sin cambios en 'data/categories.yaml'")
                    print(f"  ℹ El archivo temporal está en: {output_path}")

            print("\n✅ Sincronización completada")

        except ImportError as e:
            print(f"\n❌ Error de importación: {e}")
            print("   Asegúrate de que sync_yaml_with_repo.py y yaml_models.py estén disponibles")
        except Exception as e:
            print(f"\n❌ Error durante la sincronización: {e}")
            import traceback
            traceback.print_exc()

        input("\nPresiona Enter para continuar...")

    def handle_weekly_creation(self) -> None:
        """Maneja la creación de bitácora semanal."""
        print("\n📝 CREAR BITÁCORA SEMANAL")
        print("=" * 30)

        success = self.weekly_gen.create_next_weekly_bitacora()
        if success:
            print("\n✅ ¡Bitácora semanal creada exitosamente!")
        else:
            print("\n❌ Error al crear la bitácora semanal")

        input("\nPresiona Enter para continuar...")

    def handle_manual_weekly_creation(self) -> None:
        """Maneja la creación manual de bitácora semanal."""
        success = self.weekly_gen.create_manual_weekly_bitacora()
        if success:
            print("\n✅ ¡Bitácora semanal manual creada exitosamente!")
        else:
            print("\n❌ Error al crear la bitácora manual")

        input("\nPresiona Enter para continuar...")

    def handle_monthly_creation(self) -> None:
        """Maneja la creación de archivo mensual."""
        print("\n📋 CREAR ARCHIVO MENSUAL")
        print("=" * 30)

        success = self.monthly_gen.create_next_monthly_topics()
        if success:
            print("\n✅ ¡Archivo mensual creado exitosamente!")
        else:
            print("\n❌ Error al crear el archivo mensual")


    def handle_month_consolidation(self) -> None:
        """Maneja la consolidación de un mes completo."""
        success = self.month_consolidator.interactive_consolidate()
        input("\nPresiona Enter para continuar...")

    def handle_year_consolidation(self) -> None:
        """Maneja la consolidación de un año completo."""
        success = self.year_consolidator.interactive_consolidate()
        input("\nPresiona Enter para continuar...")

    def handle_list_files(self) -> None:
        """Maneja el listado de archivos."""
        while True:
            self.show_list_menu()
            choice = input("Selecciona una opción: ").strip()

            if choice == "1":
                clear_screen()
                print("\n📝 BITÁCORAS SEMANALES RECIENTES:")
                print("=" * 40)
                self.weekly_gen.list_recent_weeks(10)
                input("\nPresiona Enter para continuar...")

            elif choice == "2":
                clear_screen()
                print("\n📋 ARCHIVOS MENSUALES RECIENTES:")
                print("=" * 40)
                self.monthly_gen.list_recent_months(10)
                input("\nPresiona Enter para continuar...")

            elif choice == "3":
                clear_screen()
                print("\n🔍 DEBUG - TODOS LOS ARCHIVOS:")
                print("=" * 40)
                debug_files_in_directory(self.directory)
                input("\nPresiona Enter para continuar...")

            elif choice == "0":
                break

            else:
                print("❌ Opción inválida")
                input("\nPresiona Enter para continuar...")

    def handle_analyze_file(self) -> None:
        """Maneja el análisis de archivo específico."""
        print("\n🔍 ANALIZAR ARCHIVO ESPECÍFICO")
        print("=" * 35)

        # Mostrar archivos disponibles
        print("Archivos semanales recientes:")
        weekly_files = self.finder.list_weekly_files()
        for i, (filepath, year, month, week) in enumerate(weekly_files[-5:], 1):
            filename = filepath.split('/')[-1] if '/' in filepath else filepath.split('\\')[-1]
            print(f"  {i}. {filename}")

        print("\nArchivos mensuales recientes:")
        monthly_files = self.finder.list_monthly_files()
        for i, (filepath, year, month) in enumerate(monthly_files[-3:], 6):
            filename = filepath.split('/')[-1] if '/' in filepath else filepath.split('\\')[-1]
            print(f"  {i}. {filename}")

        print("\nO escribe el nombre completo del archivo:")

        choice = input("Selecciona archivo (número o nombre): ").strip()

        filepath = None

        # Intentar obtener por número
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= 5 and choice_num <= len(weekly_files):
                filepath = weekly_files[choice_num - 1][0]
            elif 6 <= choice_num <= 8 and (choice_num - 6) < len(monthly_files):
                filepath = monthly_files[choice_num - 6][0]
        except ValueError:
            # Intentar como nombre de archivo
            import os
            if os.path.exists(choice):
                filepath = choice
            elif os.path.exists(os.path.join(self.directory, choice)):
                filepath = os.path.join(self.directory, choice)

        if filepath:
            debug_content_parsing(filepath)
        else:
            print("❌ Archivo no encontrado")

        input("\nPresiona Enter para continuar...")

    def handle_debug_tools(self) -> None:
        """Maneja las herramientas de debug."""
        while True:
            self.show_debug_menu()
            choice = input("Selecciona una opción: ").strip()

            if choice == "1":
                filename = input("Nombre del archivo a analizar: ").strip()
                import os
                filepath = filename if os.path.exists(filename) else os.path.join(self.directory, filename)
                if os.path.exists(filepath):
                    debug_content_parsing(filepath)
                else:
                    print("❌ Archivo no encontrado")
                input("\nPresiona Enter para continuar...")

            elif choice == "2":
                debug_files_in_directory(self.directory)
                input("\nPresiona Enter para continuar...")

            elif choice == "3":
                test_emoji_pattern()
                input("\nPresiona Enter para continuar...")

            elif choice == "4":
                filename = input("Nombre del archivo para calcular fechas: ").strip()
                import os
                from brackets.utils.legacy_utils import safe_file_read
                from brackets.utils.content_parser import ContentParser

                filepath = filename if os.path.exists(filename) else os.path.join(self.directory, filename)
                if os.path.exists(filepath):
                    content = safe_file_read(filepath)
                    if content:
                        parser = ContentParser(content)
                        dates = parser.get_next_week_dates()
                        print("📅 Próximas fechas calculadas:")
                        from brackets.config import WEEKDAYS
                        for i, date in enumerate(dates):
                            print(f"  {WEEKDAYS[i]}: {date.strftime('%d/%m/%Y')}")
                else:
                    print("❌ Archivo no encontrado")
                input("\nPresiona Enter para continuar...")

            elif choice == "0":
                break

            else:
                print("❌ Opción inválida")

    def handle_category_management(self) -> None:
        """Maneja la gestión de categorías y documentos."""
        # Lazy import de CategoryManager
        from brackets.managers.category_manager import CategoryManager

        if self.category_manager is None:
            self.category_manager = CategoryManager(self.data_dir)

        while True:
            clear_screen()
            print(f"\n📂 GESTIONAR CATEGORÍAS Y DOCUMENTOS - {self.vault_name}")
            print("=" * 60)
            print("1. 📄 Crear nuevo documento")
            print("2. 📚 Ver todas las categorías")
            print("3. 🔍 Explorar categorías")
            print("0. ↩️ Volver al menú principal")
            print("-" * 60)

            choice = input("Opción: ").strip()

            if choice == "1":
                if self.category_manager.interactive_create_document():
                    print("\n✅ Documento creado exitosamente")
                else:
                    print("\n❌ No se pudo crear el documento")
                input("\nPresiona Enter para continuar...")

            elif choice == "2":
                self.category_manager.list_all_categories()
                input("\nPresiona Enter para continuar...")

            elif choice == "3":
                category = self.category_manager.select_category()
                if category:
                    subcategory = self.category_manager.select_subcategory(category)
                    if subcategory:
                        print(f"\n✅ Seleccionado: {category.get('name')} → {subcategory.get('name')}")
                input("\nPresiona Enter para continuar...")

            elif choice == "0":
                break

            else:
                print("❌ Opción inválida")

    def handle_file_rename(self) -> None:
        """Maneja la búsqueda y reemplazo global de texto."""
        if self.file_rename_manager is None:
            self.file_rename_manager = FileRenameManager(self.notes_root)

        # Mostrar menú de opciones
        while True:
            clear_screen()
            print(f"\n🔍 BÚSQUEDA Y REEMPLAZO - {self.vault_name}")
            print("=" * 60)
            print("1. 🔍 Búsqueda y reemplazo global")
            print("   (Busca y reemplaza texto en nombres y contenido)")
            print("2. 📁 Renombrar archivo específico")
            print("   (Renombra archivo y actualiza referencias)")
            print("0. ↩️ Volver al menú principal")
            print("-" * 60)

            choice = input("Opción: ").strip()

            if choice == "1":
                self.file_rename_manager.interactive_global_replace()
                input("\nPresiona Enter para continuar...")
                break
            elif choice == "2":
                self.file_rename_manager.interactive_rename()
                input("\nPresiona Enter para continuar...")
                break
            elif choice == "0":
                break
            else:
                print("❌ Opción inválida")

    def handle_configuration(self) -> None:
        """Maneja la configuración viva (horarios y calendario)."""
        while True:
            clear_screen()
            print(f"\n⚙️ CONFIGURACIÓN - {self.vault_name}")
            print("=" * 50)
            print("1. 👁️ Ver configuración actual")
            print("2. 🏢 Ajustar patrón de trabajo")
            print("3. 🎉 Gestionar festivos")
            print("4. 🏖️ Gestionar vacaciones")
            print("0. ↩️ Volver al menú principal")
            print("-" * 50)

            choice = input("Opción: ").strip()

            if choice == "1":
                self._show_configuration_overview()
                input("\nPresiona Enter para continuar...")
            elif choice == "2":
                self._configure_work_pattern()
            elif choice == "3":
                self._configure_holidays()
            elif choice == "4":
                self._configure_vacations()
            elif choice == "0":
                break
            else:
                print("❌ Opción inválida")

    def _show_configuration_overview(self) -> None:
        clear_screen()
        print(f"\n👁️ CONFIGURACIÓN ACTUAL - {self.vault_name}")
        print("=" * 55)
        print(self.settings.describe_work_pattern())

        holidays = self.settings.list_holidays()
        if holidays:
            print("\nFestivos configurados:")
            for i, item in enumerate(holidays, 1):
                print(f" {i}. {item.get('date')} - {item.get('name', '')}")
        else:
            print("\nFestivos configurados: ninguno")

        vacations = self.settings.list_vacations()
        if vacations:
            print("\nVacaciones configuradas:")
            for i, item in enumerate(vacations, 1):
                print(f" {i}. {item.get('start')} → {item.get('end')} - {item.get('name', '')}")
        else:
            print("\nVacaciones configuradas: ninguna")

    def _configure_work_pattern(self) -> None:
        day_map = {
            "1": "monday",
            "2": "tuesday",
            "3": "wednesday",
            "4": "thursday",
            "5": "friday",
        }
        while True:
            clear_screen()
            print(f"\n🏢 PATRÓN DE TRABAJO - {self.vault_name}")
            print("-" * 50)
            print(self.settings.describe_work_pattern())
            print("\n1. Cambiar día específico")
            print("2. Configurar día alterno par/impar")
            print("3. Restaurar valores por defecto")
            print("0. Volver")
            choice = input("Opción: ").strip()

            if choice == "1":
                day_choice = input("Selecciona día (1=L, 2=M, 3=X, 4=J, 5=V): ").strip()
                day_key = day_map.get(day_choice)
                if not day_key:
                    print("❌ Día inválido")
                    continue
                location = self._prompt_location("Ubicación para el día")
                if not location:
                    continue
                if location == "alternating":
                    even_loc = self._prompt_location("Ubicación semana par")
                    odd_loc = self._prompt_location("Ubicación semana impar")
                    if even_loc and odd_loc:
                        self.settings.set_alternating(day_key, even_loc, odd_loc)
                        print("✅ Día alterno actualizado")
                else:
                    try:
                        self.settings.set_day_location(day_key, location)
                        print("✅ Día actualizado")
                    except Exception as e:
                        print(f"❌ {e}")
            elif choice == "2":
                day_choice = input("Día alterno (1=L,2=M,3=X,4=J,5=V): ").strip()
                day_key = day_map.get(day_choice)
                if not day_key:
                    print("❌ Día inválido")
                    continue
                even_loc = self._prompt_location("Ubicación semana par")
                odd_loc = self._prompt_location("Ubicación semana impar")
                if even_loc and odd_loc:
                    try:
                        self.settings.set_alternating(day_key, even_loc, odd_loc)
                        print("✅ Alternancia actualizada")
                    except Exception as e:
                        print(f"❌ {e}")
            elif choice == "3":
                self.settings.reset_defaults()
                print("✅ Patrón restaurado a valores por defecto")
            elif choice == "0":
                break
            else:
                print("❌ Opción inválida")

    def _configure_holidays(self) -> None:
        while True:
            holidays = self.settings.list_holidays()
            clear_screen()
            print(f"\n🎉 FESTIVOS - {self.vault_name}")
            print("-" * 50)
            if holidays:
                for i, item in enumerate(holidays, 1):
                    print(f" {i}. {item.get('date')} - {item.get('name', '')}")
            else:
                print(" No hay festivos configurados")

            choice = input("(A)ñadir/actualizar, (E)ditar nombre, (D)elete, 0 volver: ").strip().lower()
            if choice == "0":
                break
            if choice == "a":
                date_str = input("Fecha (YYYY-MM-DD): ").strip()
                name = input("Nombre: ").strip() or "Festivo"
                try:
                    self.settings.add_or_update_holiday(date_str, name)
                    print("✅ Festivo guardado")
                except Exception as e:
                    print(f"❌ {e}")
            elif choice == "e":
                index = input("Número a editar: ").strip()
                try:
                    idx = int(index) - 1
                    if 0 <= idx < len(holidays):
                        name = input("Nuevo nombre: ").strip() or holidays[idx].get('name', 'Festivo')
                        self.settings.add_or_update_holiday(holidays[idx].get('date'), name)
                        print("✅ Festivo actualizado")
                    else:
                        print("❌ Índice inválido")
                except ValueError:
                    print("❌ Índice inválido")
            elif choice == "d":
                index = input("Número a eliminar: ").strip()
                try:
                    idx = int(index) - 1
                    self.settings.delete_holiday(idx)
                    print("✅ Festivo eliminado")
                except ValueError:
                    print("❌ Índice inválido")
            else:
                print("❌ Opción inválida")

    def _configure_vacations(self) -> None:
        while True:
            vacations = self.settings.list_vacations()
            clear_screen()
            print(f"\n🏖️ VACACIONES - {self.vault_name}")
            print("-" * 50)
            if vacations:
                for i, item in enumerate(vacations, 1):
                    print(f" {i}. {item.get('start')} → {item.get('end')} - {item.get('name', '')}")
            else:
                print(" No hay vacaciones configuradas")

            choice = input("(A)ñadir/actualizar, (E)ditar nombre, (D)elete, 0 volver: ").strip().lower()
            if choice == "0":
                break
            if choice == "a":
                start = input("Inicio (YYYY-MM-DD): ").strip()
                end = input("Fin (YYYY-MM-DD): ").strip()
                name = input("Nombre: ").strip() or "Vacaciones"
                try:
                    self.settings.add_or_update_vacation(start, end, name)
                    print("✅ Vacaciones guardadas")
                except Exception as e:
                    print(f"❌ {e}")
            elif choice == "e":
                index = input("Número a editar: ").strip()
                try:
                    idx = int(index) - 1
                    if 0 <= idx < len(vacations):
                        vac = vacations[idx]
                        name = input("Nuevo nombre: ").strip() or vac.get('name', 'Vacaciones')
                        self.settings.add_or_update_vacation(vac.get('start'), vac.get('end'), name)
                        print("✅ Vacaciones actualizadas")
                    else:
                        print("❌ Índice inválido")
                except ValueError:
                    print("❌ Índice inválido")
            elif choice == "d":
                index = input("Número a eliminar: ").strip()
                try:
                    idx = int(index) - 1
                    self.settings.delete_vacation(idx)
                    print("✅ Vacaciones eliminadas")
                except ValueError:
                    print("❌ Índice inválido")
            else:
                print("❌ Opción inválida")

    def _prompt_location(self, label: str) -> Optional[str]:
        print(f"{label}: 1=🏠 Casa, 2=🚗 Oficina, 3=💻 Remoto, 4=Alterna par/impar")
        value = input("Elige opción: ").strip()
        mapping = {
            "1": "home",
            "2": "office",
            "3": "remote",
            "4": "alternating",
        }
        if value not in mapping:
            print("❌ Opción inválida")
            return None
        return mapping[value]

    def show_help(self) -> None:
        """Muestra información de ayuda."""
        clear_screen()
        print(f"\n❓ AYUDA - GENERADOR DE BITÁCORAS")
        print(f"📁 Vault: {self.vault_name}")
        print("=" * 55)
        bitacoras_status = "activadas" if self.bitacoras_enabled else "desactivadas"
        print("""
📝 BITÁCORAS SEMANALES:
• Formato: [YYYY][MM]WeekXX.md
• Contienen sección TOPICS con tareas pendientes
• Incluyen días de trabajo con ubicación (🏠 casa / 🚗 oficina)
• Se transfieren automáticamente las tareas pendientes

📋 ARCHIVOS MENSUALES:
• Formato: [YYYY][MM]MonthTopics.md
• Contienen objetivos y proyectos del mes
• Se limpian automáticamente las tareas completadas [x]
• Incluyen emoji de estación según el mes

🏢 PATRÓN DE TRABAJO:
• Configurable en el menú "⚙️ Configuración"
• Fuente de verdad: data/work_calendar.yaml
• Día alterno (par/impar) editable
• Festivos y vacaciones marcan el día como 🏖️ automáticamente

🔧 FUNCIONES PRINCIPALES:
• Creación automática de siguiente bitácora
• Transferencia de tareas pendientes
• Cálculo automático de fechas
• Limpieza de tareas completadas
• Herramientas de debug y análisis
        """)
        print("\n🧩 MODO DE USO:")
        print(f"• Estado actual de bitácoras: {bitacoras_status}")
        print("• Puedes activar/desactivar bitácoras en data/config.yaml")
        print("• Clave: feature_flags.bitacoras_enabled (true/false)")
        input("\nPresiona Enter para continuar...")

    def run(self) -> None:
        """Ejecuta el menú principal."""
        while True:
            try:
                self.show_main_menu()
                choice = input("Selecciona una opción: ").strip()

                if choice == "1":
                    self.handle_generation_menu()

                elif choice == "2":
                    self.handle_consolidation_menu()

                elif choice == "3":
                    self.handle_file_management_menu()

                elif choice == "4":
                    self.handle_tools_menu()

                elif choice == "5":
                    self.handle_configuration()

                elif choice == "6":
                    self.show_help()

                elif choice == "0":
                    clear_screen()
                    print("\n👋 ¡Hasta luego!")
                    break

                else:
                    print("❌ Opción inválida. Por favor, selecciona una opción del menú.")
                    input("Presiona Enter para continuar...")

            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"\n❌ Error inesperado: {e}")
                print("Por favor, reporta este error si persiste.")
                input("Presiona Enter para continuar...")
            except Exception as e:
                print(f"\n❌ Error inesperado: {e}")
                print("Por favor, reporta este error si persiste.")
                input("Presiona Enter para continuar...")


def main():
    """Función principal del script."""
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description="Generador de bitácoras semanales y archivos mensuales",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py                             # Modo interactivo (gestor de vaults)
  python main.py -d .                        # Modo interactivo (vault actual)
  python main.py --weekly                   # Crear bitácora semanal directamente
  python main.py --monthly                  # Crear archivo mensual directamente
    python main.py --timer                    # Abrir Pomodoro Timer
  python main.py --consolidate 2025-07      # Consolidar mes específico
  python main.py --consolidate-year 2025    # Consolidar año completo
  python main.py --list                     # Listar archivos recientes
  python main.py --debug                    # Información de debug
        """
    )

    parser.add_argument(
        "--directory", "-d",
        default=None,
        help="Directorio del vault (por defecto: selector de vaults)"
    )

    parser.add_argument(
        "--weekly", "-w",
        action="store_true",
        help="Crear bitácora semanal directamente"
    )

    parser.add_argument(
        "--monthly", "-m",
        action="store_true",
        help="Crear archivo mensual directamente"
    )

    parser.add_argument(
        "--timer",
        action="store_true",
        help="Abrir Pomodoro Timer"
    )

    parser.add_argument(
        "--consolidate", "-c",
        metavar="YYYY-MM",
        help="Consolidar todos los archivos de un mes específico (formato: YYYY-MM)"
    )

    parser.add_argument(
        "--consolidate-year",
        metavar="YYYY",
        help="Consolidar todos los meses de un año específico (formato: YYYY)"
    )

    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="Listar archivos recientes"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Mostrar información de debug"
    )

    parser.add_argument(
        "--test-emoji",
        action="store_true",
        help="Probar patrón de emojis de trabajo"
    )

    parser.add_argument(
        "--analyze",
        metavar="ARCHIVO",
        help="Analizar contenido de un archivo específico"
    )

    args = parser.parse_args()

    # Determinar directorio del vault
    vault_directory = args.directory

    # Si no se pasó --directory y no hay flags de acción, mostrar VaultManager
    has_action_flags = any([
        args.weekly, args.monthly, args.timer, args.consolidate, args.consolidate_year,
        args.list, args.debug, args.test_emoji, args.analyze
    ])

    if vault_directory is None and not has_action_flags:
        # Modo gestor de vaults
        from brackets.managers.vault_manager import VaultManager
        from brackets.utils.vault_creator import create_new_vault

        # Buscar workspace root (directorio padre del directorio actual si contiene brackets/)
        workspace_root = os.getcwd()
        if os.path.exists(os.path.join(workspace_root, "brackets", "brackets")):
            # Estamos en workspace root
            pass
        elif os.path.exists(os.path.join(workspace_root, "..", "brackets", "brackets")):
            # Estamos en un vault dentro del workspace
            workspace_root = os.path.abspath(os.path.join(workspace_root, ".."))

        vault_mgr = VaultManager(workspace_root)

        while True:
            selected = vault_mgr.show_vault_menu()

            if selected is None:
                # Usuario salió
                print("\n👋 ¡Hasta luego!")
                sys.exit(0)

            elif selected == 'CREATE_NEW':
                # Crear nuevo vault
                new_vault_path = create_new_vault(workspace_root)
                if new_vault_path:
                    vault_mgr.refresh_vaults()
                    vault_directory = new_vault_path
                    break
                # Si cancela, vuelve al menú
                continue

            else:
                # Vault seleccionado
                vault_directory = selected
                break

    elif vault_directory is None:
        # Si hay flags de acción pero no --directory, usar directorio actual
        vault_directory = "."

    # Crear manager con el vault seleccionado
    manager = BitacoraManager(vault_directory)

    # Manejar argumentos de línea de comandos
    if args.weekly:
        if not manager.bitacoras_enabled:
            print("❌ Bitácoras desactivadas por configuración (feature_flags.bitacoras_enabled=false)")
            sys.exit(1)
        print("🗓️ Creando bitácora semanal...")
        success = manager.weekly_gen.create_next_weekly_bitacora()
        sys.exit(0 if success else 1)

    elif args.monthly:
        if not manager.bitacoras_enabled:
            print("❌ Bitácoras desactivadas por configuración (feature_flags.bitacoras_enabled=false)")
            sys.exit(1)
        print("📋 Creando archivo mensual...")
        success = manager.monthly_gen.create_next_monthly_topics()
        sys.exit(0 if success else 1)

    elif args.timer:
        from brackets.modules.pomodoro_timer import run_pomodoro_standalone
        run_pomodoro_standalone(vault_directory)
        sys.exit(0)

    elif args.consolidate:
        if not manager.bitacoras_enabled:
            print("❌ Bitácoras desactivadas por configuración (feature_flags.bitacoras_enabled=false)")
            sys.exit(1)
        print(f"📦 Consolidando mes {args.consolidate}...")
        import re
        match = re.match(r'(\d{4})-(\d{2})', args.consolidate)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            success = manager.month_consolidator.consolidate_month(year, month)
            sys.exit(0 if success else 1)
        else:
            print("❌ Formato inválido. Use YYYY-MM (ejemplo: 2025-07)")
            sys.exit(1)

    elif args.consolidate_year:
        if not manager.bitacoras_enabled:
            print("❌ Bitácoras desactivadas por configuración (feature_flags.bitacoras_enabled=false)")
            sys.exit(1)
        print(f"📅 Consolidando año {args.consolidate_year}...")
        try:
            year = int(args.consolidate_year)
            success = manager.year_consolidator.consolidate_year(year)
            sys.exit(0 if success else 1)
        except ValueError:
            print("❌ Formato inválido. Use YYYY (ejemplo: 2025)")
            sys.exit(1)

    elif args.list:
        print("📊 Archivos recientes:")
        print("\n📝 Bitácoras semanales:")
        manager.weekly_gen.list_recent_weeks(10)
        print("\n📋 Archivos mensuales:")
        manager.monthly_gen.list_recent_months(5)
        sys.exit(0)

    elif args.debug:
        debug_files_in_directory(vault_directory)
        sys.exit(0)

    elif args.test_emoji:
        test_emoji_pattern()
        sys.exit(0)

    elif args.analyze:
        import os
        filepath = args.analyze
        if not os.path.exists(filepath):
            filepath = os.path.join(vault_directory, args.analyze)

        if os.path.exists(filepath):
            debug_content_parsing(filepath)
        else:
            print(f"❌ Archivo no encontrado: {args.analyze}")
            sys.exit(1)
        sys.exit(0)

    else:
        # Modo interactivo por defecto
        manager.run()


if __name__ == "__main__":
    main()
