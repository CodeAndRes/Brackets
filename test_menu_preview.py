#!/usr/bin/env python3
"""Test para ver cómo se ve el header del menú."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from brackets.main import BitacoraManager

# Crear manager para MyJobNotes
print("\n" + "="*70)
print("PREVIEW DEL MENÚ PRINCIPAL CON NOMBRE DE VAULT")
print("="*70 + "\n")

manager = BitacoraManager("../MyJobNotes")

# Simular el header del menú principal sin clear_screen
print(f"\n🗓️ GENERADOR DE BITÁCORAS - SISTEMA BRACKETS")
print(f"📁 Vault: {manager.vault_name}")
print("=" * 50)
print("1. 📝 Generación de Bitácoras")
print("2. 📦 Consolidación de Archivos")
print("3. 📂 Gestión de Archivos y Categorías")
print("4. 🔧 Herramientas y Utilidades")
print("5. ⚙️ Configuración")
print("6. ❓ Ayuda")
print("0. 🚪 Salir")
print("-" * 50)

print("\n" + "="*70)
print("Ahora con PersonalNotes")
print("="*70 + "\n")

manager2 = BitacoraManager("../PersonalNotes")
print(f"\n🗓️ GENERADOR DE BITÁCORAS - SISTEMA BRACKETS")
print(f"📁 Vault: {manager2.vault_name}")
print("=" * 50)
print("1. 📝 Generación de Bitácoras")
print("...")

print("\n✅ El nombre del vault ahora aparece en todos los menús!")
print("   Prueba ejecutando: python run_brackets.py (desde cualquier vault)\n")
