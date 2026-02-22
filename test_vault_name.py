#!/usr/bin/env python3
"""Test para ver el nombre del vault en el menú."""

import sys
import os

# Agregar el path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from brackets.main import BitacoraManager

# Test con diferentes vaults
test_vaults = [
    ("../MyJobNotes", "MyJobNotes esperado"),
    ("../PersonalNotes", "PersonalNotes esperado"),
    ("../test-vault", "test-vault esperado"),
    (".", "brackets esperado (directorio actual)"),
]

print("\n🧪 PRUEBA DE NOMBRE DE VAULT EN MENÚ\n")
print("=" * 60)

for vault_path, description in test_vaults:
    abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), vault_path))

    if not os.path.exists(os.path.join(abs_path, "data", "config.yaml")):
        print(f"❌ {description}: No existe config.yaml")
        continue

    try:
        manager = BitacoraManager(vault_path)
        print(f"✅ {description}")
        print(f"   📁 Vault detectado: '{manager.vault_name}'")
        print(f"   📂 Path: {abs_path}")
        print()
    except Exception as e:
        print(f"❌ {description}: Error - {e}")
        print()

print("=" * 60)
print("\nPrueba el menú ejecutando:")
print("  cd ../MyJobNotes && python run_brackets.py")
print()
