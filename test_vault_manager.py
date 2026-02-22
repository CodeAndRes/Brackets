#!/usr/bin/env python3
"""Test simple del VaultManager para verificar detección de vaults."""

import sys
import os

# Agregar brackets al path
CORE_PATH = os.path.join(os.path.dirname(__file__), "brackets")
sys.path.insert(0, CORE_PATH)

from brackets.managers.vault_manager import VaultManager

# Crear manager
workspace = r"c:\Projects\brackets-workspace"
vm = VaultManager(workspace)

print(f"\n🔍 Buscando vaults en: {workspace}")
print(f"\n📊 Vaults encontrados: {len(vm.vaults)}\n")

for vault in vm.vaults:
    print(f"  📁 {vault['name']}")
    print(f"     Path: {vault['path']}")
    if vault['description']:
        print(f"     Desc: {vault['description']}")
    print()

print("✅ Test completado")
