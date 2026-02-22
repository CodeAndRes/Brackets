#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor de múltiples vaults.
Permite descubrir, listar y seleccionar vaults en el workspace.
"""

import os
import sys
from typing import List, Dict, Optional


class VaultManager:
    """Gestiona la detección y selección de vaults en el workspace."""

    def __init__(self, workspace_root: str = None):
        """
        Inicializa el gestor de vaults.

        Args:
            workspace_root: Raíz del workspace. Si es None, busca desde el directorio actual.
        """
        self.workspace_root = workspace_root or os.getcwd()
        self.vaults = self._discover_vaults()

    def _is_valid_vault(self, path: str) -> bool:
        """
        Verifica si un directorio es un vault válido.

        Args:
            path: Ruta del directorio a verificar

        Returns:
            True si es un vault válido (tiene data/config.yaml)
        """
        config_path = os.path.join(path, "data", "config.yaml")
        return os.path.exists(config_path)

    def _discover_vaults(self) -> List[Dict[str, str]]:
        """
        Descubre todos los vaults en el workspace.

        Returns:
            Lista de diccionarios con info de cada vault: {name, path, description}
        """
        vaults = []

        # Buscar en el workspace (1 nivel de profundidad)
        try:
            for item in os.listdir(self.workspace_root):
                item_path = os.path.join(self.workspace_root, item)

                # Ignorar directorios que no son vaults
                if item.startswith('.') or item == 'SharedContext':
                    continue

                if os.path.isdir(item_path) and self._is_valid_vault(item_path):
                    vault_info = self._get_vault_info(item_path, item)
                    vaults.append(vault_info)
        except Exception as e:
            print(f"⚠️  Error al buscar vaults: {e}")

        return sorted(vaults, key=lambda x: x['name'])

    def _get_vault_info(self, path: str, name: str) -> Dict[str, str]:
        """
        Obtiene información de un vault.

        Args:
            path: Ruta del vault
            name: Nombre del vault

        Returns:
            Diccionario con info del vault
        """
        vault_info = {
            'name': name,
            'path': path,
            'description': ''
        }

        # Intentar leer descripción desde config.yaml
        try:
            import yaml
            config_path = os.path.join(path, "data", "config.yaml")
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config and isinstance(config, dict):
                    vault_info['description'] = config.get('description', '')
        except Exception:
            pass

        return vault_info

    def show_vault_menu(self) -> Optional[str]:
        """
        Muestra el menú de selección de vaults.

        Returns:
            Ruta del vault seleccionado, 'CREATE_NEW' para crear nuevo, o None para salir
        """
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n🗃️  GESTOR DE VAULTS - SISTEMA BRACKETS")
            print("=" * 60)

            if not self.vaults:
                print("\n⚠️  No se encontraron vaults en el workspace")
                print(f"   Buscando en: {self.workspace_root}")
            else:
                print(f"\n📂 Vaults disponibles ({len(self.vaults)}):\n")
                for idx, vault in enumerate(self.vaults, 1):
                    print(f"{idx}. 📁 {vault['name']}")
                    if vault['description']:
                        print(f"   {vault['description']}")

            print(f"\n{len(self.vaults) + 1}. ➕ Crear nuevo vault")
            print("0. 🚪 Salir")
            print("-" * 60)

            choice = input("\nSelecciona una opción: ").strip()

            if choice == "0":
                return None

            # Crear nuevo vault
            if choice == str(len(self.vaults) + 1):
                return 'CREATE_NEW'

            # Seleccionar vault existente
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.vaults):
                    return self.vaults[idx]['path']
                else:
                    print("\n❌ Opción inválida")
                    input("Presiona Enter para continuar...")
            except ValueError:
                print("\n❌ Opción inválida")
                input("Presiona Enter para continuar...")

    def refresh_vaults(self):
        """Refresca la lista de vaults disponibles."""
        self.vaults = self._discover_vaults()
