#!/usr/bin/env python3
"""Category-management menu controller extracted from BitacoraManager."""

from typing import Callable, Optional


class CategoryManagementController:
    """Handle category and document management interactive flow."""

    def __init__(
        self,
        vault_name: str,
        get_category_manager_fn: Callable[[], object],
        clear_screen_fn: Callable[[], None],
        input_fn: Callable[[str], str] = input,
        print_fn: Callable[..., None] = print,
    ):
        self.vault_name = vault_name
        self.get_category_manager = get_category_manager_fn
        self.clear_screen = clear_screen_fn
        self.input = input_fn
        self.print = print_fn

    def run(self) -> None:
        """Run category-management menu loop."""
        category_manager = self.get_category_manager()

        while True:
            self.clear_screen()
            self.print(f"\n📂 GESTIONAR CATEGORÍAS Y DOCUMENTOS - {self.vault_name}")
            self.print("=" * 60)
            self.print("1. 📄 Crear nuevo documento")
            self.print("2. 📚 Ver todas las categorías")
            self.print("3. 🔍 Explorar categorías")
            self.print("0. ↩️ Volver al menú principal")
            self.print("-" * 60)

            choice = self.input("Opción: ").strip()

            if choice == "1":
                if category_manager.interactive_create_document():
                    self.print("\n✅ Documento creado exitosamente")
                else:
                    self.print("\n❌ No se pudo crear el documento")
                self.input("\nPresiona Enter para continuar...")

            elif choice == "2":
                category_manager.list_all_categories()
                self.input("\nPresiona Enter para continuar...")

            elif choice == "3":
                category = category_manager.select_category()
                if category:
                    subcategory = category_manager.select_subcategory(category)
                    if subcategory:
                        self.print(f"\n✅ Seleccionado: {category.get('name')} → {subcategory.get('name')}")
                self.input("\nPresiona Enter para continuar...")

            elif choice == "0":
                break

            else:
                self.print("❌ Opción inválida")
