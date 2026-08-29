# 📁 Directorio de Plantillas, Fallbacks y Fixtures del Motor Brackets

> ⚠️ **IMPORTANTE: Esta carpeta NO contiene datos de usuario ni bitácoras reales.**
> Los datos reales de tus notas, tareas y calendarios viven **dentro de cada Vault** (por ejemplo: MyJobNotes/data/).

---

## 🗂️ Contenido de este directorio:

| Elemento | Propósito | ¿Cuándo se usa? |
|---|---|---|
| **templates/** | Plantillas de menú especializadas (work, personal, project). | Se copian a <vault>/data/menu_config.yaml al crear un vault nuevo con vault_creator.py. |
| **menu_config.yaml** | Menú global de respaldo (*fallback*). | Solo si un Vault no tiene su propio archivo data/menu_config.yaml. |
| **work_calendar.yaml** | Calendario base por defecto (*fallback*). | Solo si un Vault no define su propio data/work_calendar.yaml. |
| **mock/** | Base de datos de prueba (fixtures simulados de 2026). | Utilizada **exclusivamente por la suite de tests unitarios** para garantizar que ningún test toque datos reales. |

---

## 🏛️ Principio de Soberanía del Vault:

1. **El Motor (brackets/):** Aporta la maquinaria de renderizado, sincronización y estas plantillas base.
2. **Tu Vault (<NombreVault>/):** Gobierna su propia configuración (data/config.yaml, data/menu_config.yaml, data/work_calendar.yaml) y almacena tus tareas y notas.
