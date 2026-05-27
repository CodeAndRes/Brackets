#!/usr/bin/env python3
"""File-rename menu controller extracted from BitacoraManager."""

from typing import Callable


class FileRenameController:
    """Handle global replace and file rename flow."""

    def __init__(
        self,
        vault_name: str,
        get_file_rename_manager_fn: Callable[[], object],
        clear_screen_fn: Callable[[], None],
        input_fn: Callable[[str], str] = input,
        print_fn: Callable[..., None] = print,
    ):
        self.vault_name = vault_name
        self.get_file_rename_manager = get_file_rename_manager_fn
        self.clear_screen = clear_screen_fn
        self.input = input_fn
        self.print = print_fn

    def run(self) -> None:
        """Run search/replace menu loop."""
        file_rename_manager = self.get_file_rename_manager()

        while True:
            self.clear_screen()
            self.print(f"\n🔍 BÚSQUEDA Y REEMPLAZO - {self.vault_name}")
            self.print("=" * 60)
            self.print("1. 🔍 Búsqueda y reemplazo global")
            self.print("   (Busca y reemplaza texto en nombres y contenido)")
            self.print("2. 📁 Renombrar archivo específico")
            self.print("   (Renombra archivo y actualiza referencias)")
            self.print("0. ↩️ Volver al menú principal")
            self.print("-" * 60)

            choice = self.input("Opción: ").strip()

            if choice == "1":
                file_rename_manager.interactive_global_replace()
                self.input("\nPresiona Enter para continuar...")
                break
            if choice == "2":
                file_rename_manager.interactive_rename()
                self.input("\nPresiona Enter para continuar...")
                break
            if choice == "0":
                break

            self.print("❌ Opción inválida")
