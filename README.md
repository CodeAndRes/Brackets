# 🗓️ Brackets - Sistema de Gestión de Bitácoras y Notas

Sistema modular y escalable para generar automáticamente bitácoras semanales, archivos mensuales de seguimiento y gestionar documentos organizados por categorías.

**Versión:** 3.0.0 - Core Independiente  
**Estado:** ✅ Producción

## 🎯 Descripción

Brackets es un sistema que combina:
- **Gestión temporal**: Bitácoras semanales y consolidaciones mensuales/anuales
- **Gestión de notas**: Categorías jerárquicas y documentos organizados
- **Herramientas**: Búsqueda/reemplazo global, renombrado inteligente, sincronización YAML

Puede funcionar en **dos modos**:
1. **Modo completo (bitácoras + notas)**: Dimensión temporal con seguimiento semanal
2. **Modo notas**: Solo gestión de documentos sin bitácoras (via `feature_flags.bitacoras_enabled: false`)

## 📁 Estructura del Repositorio

```
brackets/
├── brackets/              # 🎯 Código principal
│   ├── core/             # Clases base
│   ├── utils/            # Utilidades compartidas
│   ├── managers/         # Gestores de alto nivel
│   ├── consolidators/    # Consolidación mensual/anual
│   ├── generators/       # Generación de bitácoras
│   ├── models/           # Modelos de datos
│   └── tools/            # Herramientas auxiliares
├── run_brackets.py       # Punto de entrada principal
├── requirements.txt      # Dependencias
├── setup.py             # Instalación pip
└── README.md            # Esta documentación
```

## 🛠️ Requisitos

- Python 3.9+
- PyYAML (único requisito externo)

## 📦 Instalación

### Opción 1: Instalación pip (editable)

```bash
# Clonar repositorio
cd C:\Projects\brackets-workspace\brackets

# Instalar en modo editable
pip install -e .
```

### Opción 2: Uso directo desde vault

Desde tu vault (MyNotes, MyNotesPersonal, etc.), agrega el path del core:

```python
# En run_brackets.py de tu vault
import sys
import os

# Agregar path al core
CORE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "brackets-workspace", "brackets"))
if CORE_PATH not in sys.path:
    sys.path.insert(0, CORE_PATH)

# Ahora puedes importar
from brackets.main import BitacoraManager
```

## 🚀 Configuración del Vault

Cada vault necesita su propia estructura de datos:

### Estructura mínima

```
mi-vault/
├── data/
│   ├── config.yaml        # Configuración del vault
│   └── categories.yaml    # Categorías y documentos
├── run_brackets.py        # Script que importa el core
└── [archivos .md]         # Tus notas
```

### config.yaml mínimo

```yaml
version: "1.0.0"
system: "Brackets"

feature_flags:
  bitacoras_enabled: true  # false para modo solo-notas

paths:
  notes_root: "."
  data_dir: "data"

sync_yaml:
  include_extensions: [".md"]
  excluded_prefixes: ["[2025]", "[2026]"]
  output_file: "categories_SYNCED.yaml"
```

### categories.yaml mínimo

```yaml
version: "1.0.0"
categories: []
```

## 🎯 Uso

```bash
# Desde tu vault
cd C:\Projects\MyNotes
python run_brackets.py

# Con directorio específico
python run_brackets.py --directory .

# Ayuda
python run_brackets.py --help
```

## 📚 Documentación Completa

Para documentación detallada del sistema, ver:
- **Guía de Instalación**: SETUP.md en tu vault
- **Arquitectura**: Architecture.md en tu vault
- **Nomenclatura**: Nomenclatura.md en tu vault
- **Changelog**: Changelog.md en tu vault

## 🤝 Contribuir

Este es un proyecto personal, pero si tienes sugerencias o encuentras bugs, siéntete libre de abrir un issue.

## 📝 Licencia

Proyecto personal - Uso libre
