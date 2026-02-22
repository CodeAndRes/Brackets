#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asistente interactivo para crear nuevos vaults.
"""

import os
import sys


def create_new_vault(workspace_root: str) -> str:
    """
    Asistente interactivo para crear un nuevo vault.

    Args:
        workspace_root: Raíz del workspace donde crear el vault

    Returns:
        Ruta del vault creado, o None si se cancela
    """
    print("\n" + "=" * 60)
    print("🆕 ASISTENTE DE CREACIÓN DE VAULT")
    print("=" * 60)

    # 1. Nombre del vault
    while True:
        print("\n📝 Paso 1: Nombre del vault")
        vault_name = input("Nombre (ej: PersonalNotes, ProjectX): ").strip()

        if not vault_name:
            print("❌ El nombre no puede estar vacío")
            continue

        # Validar nombre
        if any(c in vault_name for c in r'\/:*?"<>|'):
            print("❌ El nombre contiene caracteres no válidos")
            continue

        vault_path = os.path.join(workspace_root, vault_name)

        if os.path.exists(vault_path):
            print(f"❌ Ya existe un directorio con ese nombre: {vault_path}")
            retry = input("¿Intentar con otro nombre? (S/n): ").strip().lower()
            if retry == 'n':
                return None
            continue

        break

    # 2. Descripción (opcional)
    print("\n📄 Paso 2: Descripción (opcional)")
    description = input("Descripción breve: ").strip()

    # 3. Activar bitácoras
    print("\n📅 Paso 3: Configuración de bitácoras")
    print("¿Activar generación de bitácoras semanales?")
    print("  Sí: Para notas de trabajo organizadas por semanas")
    print("  No: Solo gestión de documentos por categorías")

    while True:
        bitacoras = input("Activar bitácoras (S/n): ").strip().lower()
        if bitacoras in ['s', 'y', '', 'n']:
            bitacoras_enabled = bitacoras != 'n'
            break
        print("❌ Responde S (sí) o N (no)")

    # 4. Confirmación
    print("\n" + "-" * 60)
    print("📋 RESUMEN DE CONFIGURACIÓN:")
    print(f"  Nombre: {vault_name}")
    print(f"  Ubicación: {vault_path}")
    if description:
        print(f"  Descripción: {description}")
    print(f"  Bitácoras: {'✅ Activadas' if bitacoras_enabled else '❌ Desactivadas'}")
    print("-" * 60)

    confirm = input("\n¿Crear vault con esta configuración? (S/n): ").strip().lower()
    if confirm == 'n':
        print("❌ Creación cancelada")
        return None

    # 5. Crear estructura
    try:
        print(f"\n🔨 Creando vault '{vault_name}'...")

        # Crear directorios
        os.makedirs(vault_path, exist_ok=True)
        data_dir = os.path.join(vault_path, "data")
        os.makedirs(data_dir, exist_ok=True)

        # Crear config.yaml
        config_content = _generate_config_yaml(description, bitacoras_enabled)
        config_path = os.path.join(data_dir, "config.yaml")
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print(f"  ✅ Creado: data/config.yaml")

        # Crear categories.yaml
        categories_content = _generate_categories_yaml()
        categories_path = os.path.join(data_dir, "categories.yaml")
        with open(categories_path, 'w', encoding='utf-8') as f:
            f.write(categories_content)
        print(f"  ✅ Creado: data/categories.yaml")

        # Crear run_brackets.py
        runner_content = _generate_runner_script()
        runner_path = os.path.join(vault_path, "run_brackets.py")
        with open(runner_path, 'w', encoding='utf-8') as f:
            f.write(runner_content)
        print(f"  ✅ Creado: run_brackets.py")

        # Crear README.md
        readme_content = _generate_readme(vault_name, description, bitacoras_enabled)
        readme_path = os.path.join(vault_path, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"  ✅ Creado: README.md")

        # Crear .gitignore
        gitignore_content = _generate_gitignore()
        gitignore_path = os.path.join(vault_path, ".gitignore")
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print(f"  ✅ Creado: .gitignore")

        print(f"\n🎉 ¡Vault '{vault_name}' creado exitosamente!")
        print(f"\n📂 Ubicación: {vault_path}")
        print("\n💡 Próximos pasos:")
        print(f"   1. cd {vault_path}")
        print(f"   2. python run_brackets.py")

        input("\nPresiona Enter para continuar...")
        return vault_path

    except Exception as e:
        print(f"\n❌ Error al crear vault: {e}")
        input("\nPresiona Enter para continuar...")
        return None


def _generate_config_yaml(description: str, bitacoras_enabled: bool) -> str:
    """Genera el contenido de config.yaml."""
    desc_line = f'description: "{description}"\n' if description else ''

    return f"""# Configuración del vault
version: "1.0.0"
system: "Brackets"
{desc_line}
# Feature flags del sistema
feature_flags:
  bitacoras_enabled: {str(bitacoras_enabled).lower()}

# Rutas del vault
paths:
  notes_root: "."
  data_dir: "data"

# Configuración de sincronización de categorías
sync_yaml:
  include_extensions:
    - ".md"
  excluded_prefixes:
    - "[2025]"
    - "[2026]"
  output_file: "categories_SYNCED.yaml"
"""


def _generate_categories_yaml() -> str:
    """Genera el contenido de categories.yaml."""
    return """# Categorías de documentos
version: "1.0.0"
categories: []
"""


def _generate_runner_script() -> str:
    """Genera el contenido de run_brackets.py."""
    return """#!/usr/bin/env python3
\"\"\"Script principal de lanzamiento para el Sistema Brackets.
Este vault usa el core desde ../brackets
\"\"\"

import sys
import os

# Path al core de Brackets
CORE_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    "..",
    "brackets"
))

# Agregar el core al path
if CORE_PATH not in sys.path:
    sys.path.insert(0, CORE_PATH)

# Verificar que el core existe
if not os.path.exists(os.path.join(CORE_PATH, "brackets", "main.py")):
    print(f"❌ Error: No se encuentra el core de Brackets en: {CORE_PATH}")
    print(f"   Asegúrate de que existe: {os.path.join(CORE_PATH, 'brackets', 'main.py')}")
    sys.exit(1)

# Importar y ejecutar el main desde brackets
from brackets.main import main

if __name__ == "__main__":
    main()
"""


def _generate_readme(vault_name: str, description: str, bitacoras_enabled: bool) -> str:
    """Genera el contenido de README.md."""
    desc_section = f"\n{description}\n" if description else ""
    bitacoras_status = "✅ Activadas" if bitacoras_enabled else "❌ Desactivadas"

    return f"""# {vault_name}
{desc_section}
## 🔗 Integración con Brackets

Este vault utiliza el sistema **Brackets** para gestión de notas y documentos.

- **Core del sistema**: `../brackets/`
- **Bitácoras semanales**: {bitacoras_status}

## 🚀 Uso

```bash
# Desde este directorio
python run_brackets.py

# Con opciones
python run_brackets.py --help
python run_brackets.py --weekly
python run_brackets.py --list
```

## ⚙️ Configuración

La configuración específica de este vault está en:
- `data/config.yaml` - Configuración general y feature flags
- `data/categories.yaml` - Estructura de categorías de documentos

## 📚 Documentación

Documentación completa del sistema Brackets:
- **Core**: `../brackets/README.md`
- **Workspace**: `../SharedContext/HANDOFF_GLOBAL.md`
"""


def _generate_gitignore() -> str:
    """Genera el contenido de .gitignore."""
    return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Virtual environments
venv/
ENV/
env/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Brackets related
brackets/
categories_SYNCED.yaml
"""
