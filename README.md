# 🗓️ Brackets

<div align="center">

**Sistema modular de gestión de bitácoras semanales y notas organizadas**

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-3.0.0-green.svg)](https://github.com/CodeAndRes/Brackets/releases)

[Características](#-características) •
[Instalación](#-instalación) •
[Uso Rápido](#-uso-rápido) •
[Documentación](#-documentación)

</div>

---

## 🎯 ¿Qué es Brackets?

Brackets es un sistema Python que combina **gestión temporal con organización estructurada de notas**:

- 📝 **Bitácoras semanales** con transferencia automática de tareas pendientes
- 📦 **Consolidación mensual/anual** para archivar contenido
- 📂 **Categorías jerárquicas** infinitas para organizar documentos
- 🔍 **Búsqueda y reemplazo global** en nombres y contenido
- ⚙️ **Configuración flexible** por vault (horarios, festivos, paths)
- 🧩 **Modo opcional sin bitácoras** - úsalo solo para gestionar notas

## ✨ Características

### 🖥️ Hub Diario y Navegación Interactiva
- **Dashboard en tiempo real**: Visualiza la semana activa, topics en curso, tareas de hoy, tareas semanales sin día fijo y notas.
- **Navegación ágil por categorías (Opción B)**: Menú armonizado con accesos directos (`[t]` Tareas, `[n]` Notas, `[p]` Proyectos, `[d]` Días) y footer limpio.
- **Sincronización Bidireccional Markdown ➔ YAML**: Edita tus archivos `.md` en cualquier editor y Brackets reconcilia los cambios automáticamente sin duplicidades.

### 🗃️ Base de Datos Relacional YAML-First
- **Fuente de verdad estructurada**: Todas las entidades viven en `data/tables/` (`projects.yaml`, `topics.yaml`, `tasks.yaml`, `notes.yaml`, `definitions.yaml`, `recurring_tasks.yaml`).
- **Jerarquía `Proyecto ➔ Topic ➔ Tarea / Nota`**: Tópicos semanales enmarcados en proyectos, con asignación y herencia relacional directa.
- **Backlog de Proyecto**: Gestión interactiva de tareas por proyecto, con filtros pendientes/completadas y reactivación.

### 🔄 Tareas Recurrentes y Ciclo de Vida Semanal
- **Reuniones y rutinas programadas**: Configuración de tareas para días específicos (ej: *Daily S^3* los L-X-V) o intervalos (ej: *Renovar accesos* cada 4 semanas). Inyección idempotente.
- **Sección `## 📋Week Tasks`**: Tareas de la semana sin día fijo.
- **Rollover con regla de 2 semanas**: Las tareas pendientes de la semana previa se traspasan a la nueva semana; si cumplen 2 semanas sin resolverse, se retiran de la semana y quedan archivadas en el Backlog de su Proyecto.

### 📝 Generación de Bitácoras
- **Bitácoras semanales automáticas**: Calcula fechas y transfiere tareas pendientes
- **Creación manual**: Para vaults nuevos o control total de fechas
- **Gestión de peso**: Seguimiento opcional
- **Patrón de trabajo configurable**: Teletrabajo/presencial con semanas alternas

### 📦 Consolidación
- **Mensual**: Agrupa todas las semanas de un mes en un archivo
- **Anual**: Consolida todo el año basándose en archivos mensuales
- **Orden inverso**: Contenido más reciente primero
- **Jerarquía clara**: Año > Meses > Semanas > Días

### 📂 Gestión de Documentos y Categorías
- **Categorías jerárquicas**: Anidación infinita (Categoría → Sub → Sub → ...)
- **Nomenclatura automática**: `[CATEGORIA][SUBCATEGORIA]nombre.ext`
- **Múltiples extensiones**: `.md`, `.py`, `.sql`, `.yaml`, etc.
- **Navegación interactiva**: Menú guiado para crear documentos

### 🔧 Herramientas
- **Timer Pomodoro v1**: Gestión de sesiones de foco y descanso integrada en CLI
- **Búsqueda y reemplazo global**: En contenido y nombres de archivo
- **Renombrado inteligente**: Actualiza referencias automáticamente
- **Sincronización YAML**: Mantiene `categories.yaml` actualizado con el repo

---

## 🛠️ Requisitos e Instalación

- **Python 3.9+**
- **PyYAML** (único requisito externo)

### Opción 1: Clonar y usar directamente

```bash
git clone https://github.com/CodeAndRes/Brackets.git
cd Brackets
pip install pyyaml
python run_brackets.py
```

### Opción 2: Instalación pip (editable)

```bash
git clone https://github.com/CodeAndRes/Brackets.git
cd Brackets
pip install -e .
```

### Opción 3: Integrar con vault existente

Si tienes un vault de notas, crea un `run_brackets.py`:

```python
#!/usr/bin/env python3
import sys
import os

# Path al core de Brackets
CORE_PATH = r"C:\ruta\a\Brackets"
if CORE_PATH not in sys.path:
    sys.path.insert(0, CORE_PATH)

from brackets.main import main

if __name__ == "__main__":
    main()
```

## 🎯 Uso Rápido

### Crear tu primer vault

```bash
# 1. Crear estructura
mkdir mi-vault
cd mi-vault
mkdir data
```

```yaml
# 2. Crear data/config.yaml
version: "1.0.0"
system: "Brackets"

feature_flags:
  bitacoras_enabled: true

paths:
  notes_root: "."
  data_dir: "data"

sync_yaml:
  include_extensions: [".md"]
  excluded_prefixes: []
  output_file: "categories_SYNCED.yaml"
```

```yaml
# 3. Crear data/categories.yaml
version: "1.0.0"
categories: []
```

```bash
# 4. Ejecutar (desde el directorio de Brackets)
cd ../Brackets
python run_brackets.py --directory ../mi-vault
```

### Menú Interactivo

```bash
python run_brackets.py
```

Opciones disponibles:
- 📝 Crear bitácora semanal (automática desde última semana)
- ✏️ Crear bitácora manual (especifica fechas)
- 📋 Crear archivo mensual
- 📦 Consolidar mes completo
- 📅 Consolidar año completo
- 📂 Gestionar categorías y documentos
- 🔍 Búsqueda y reemplazo global
- ⚙️ Configuración (horarios, festivos, vacaciones)

### Línea de Comandos

```bash
# Crear bitácora semanal directamente
python run_brackets.py --weekly

# Listar archivos recientes
python run_brackets.py --list

# Consolidar mes específico
python run_brackets.py --consolidate 2026-02

# Consolidar año completo
python run_brackets.py --consolidate-year 2026

# Ver ayuda
python run_brackets.py --help
```

## 📁 Estructura del Repositorio

```
brackets/
├── brackets/              # 🎯 Código principal
│   ├── core/             # Clases base y núcleo
│   ├── utils/            # Utilidades compartidas
│   ├── managers/         # Gestores de alto nivel
│   │   ├── category_manager.py
│   │   ├── settings_manager.py
│   │   └── file_rename_manager.py
│   ├── consolidators/    # Consolidación mensual/anual
│   ├── generators/       # Generación de bitácoras
│   ├── models/           # Modelos de datos
│   ├── tools/            # Herramientas auxiliares
│   └── tests/            # Tests automatizados
├── run_brackets.py       # Punto de entrada
├── requirements.txt      # Dependencias
├── setup.py             # Instalación pip
├── README.md
└── LICENSE
```

## 📋 Ejemplos

### Bitácora Semanal Generada

```markdown
# 🗓️Week 8 108.0

## ✅Topics
  - [x] Reclamar conexión de InfluxDB
  - [ ] Empezar a construir Dashboards en Grafana
  ---

## 📝Notes
- ### Upgrade versión InfluxDB
  - @MarcCristany propone hacer un upgrade
  - @FerranVallalta y @PabloMartinez de acuerdo
  ---

## 🚗17 (Oficina)
  - [ ] Revisión de base de datos
  - [x] Reunión de coordinación

<!-- Definiciones -->
[🎫ATLM-12682]: https://mangospain.atlassian.net/browse/ATLM-12682
```

### Estructura de Categorías

```yaml
categories:
  - name: "🎓LEARNING"
    description: "Aprendizaje y formación"
    subcategories:
      - name: "PYTHON"
        subcategories:
          - name: "ADVANCED"
            documents:
              - "decorators.md"
              - "async_io.md"
      - name: "GIT"
        documents:
          - "commands.md"
          - "workflows.md"
  
  - name: "📋PROJECTS"
    description: "Proyectos activos"
    subcategories:
      - name: "WEB"
        documents:
          - "api_design.md"
```

### Archivos Generados

```
vault/
├── [2026][02]Week08.md              # Bitácora semanal (renderizada)
├── [2026][02].md                    # Consolidado mensual
├── [2026].md                        # Consolidado anual
├── [🎓LEARNING][PYTHON]decorators.md
├── [🎓LEARNING][GIT]commands.md
└── [📋PROJECTS][WEB]api_design.md
```

## ⚙️ Configuración Avanzada

### Feature Flags

```yaml
feature_flags:
  bitacoras_enabled: false  # Desactiva modo temporal, solo notas
```

### Paths Personalizados

```yaml
paths:
  notes_root: "notes"       # Carpeta con archivos .md
  data_dir: "data"          # Carpeta con YAML de configuración y tablas
```

### Horario de Trabajo

```yaml
# En data/work_calendar.yaml
work_pattern:
  monday:
    location: "casa"
    emoji: "🏠"
  tuesday:
    location: "oficina"
    emoji: "🚗"
  # ...
  friday:
    location: "alternativo"
    semana_par: "casa"
    semana_impar: "oficina"
```

## 🧪 Tests

```bash
# Ejecutar suite completa (118 tests)
python brackets/tests/test_suite.py

# En Windows (PowerShell con codificación UTF-8)
$env:PYTHONUTF8=1; python brackets/tests/test_suite.py
```

## 🤝 Contribuir

¿Encontraste un bug o tienes una idea? ¡Abre un issue!

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: amazing feature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

Desarrollado por [CodeAndRes](https://github.com/CodeAndRes) como sistema personal de gestión de bitácoras y notas.

---

<div align="center">

**[⬆ Volver arriba](#-brackets)**

Made with ❤️ and Python

</div>
