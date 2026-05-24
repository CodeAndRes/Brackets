# Propuesta Técnica: Desacoplamiento y Dinamismo de Menús (Brackets v0.3)

## 1. Esquema YAML para Menús Dinámicos
El objetivo es que `main.py` actúe como un motor de renderizado agnóstico a la estructura, leyendo la configuración de un archivo `menu_config.yaml`.

### Definición del Esquema
```yaml
# menu_config.yaml
menus:
  principal:
    title: "M E N Ú  P R I N C I P A L"
    items:
      - label: "Bitácoras"
        key: "b"
        action: "submenu"
        target: "menu_bitacoras"
      - label: "Consolidar Vault"
        key: "c"
        action: "exec"
        command: "scripts.consolidate.run"
        context_tag: "active_vault"  # Solo visible si hay un vault detectado
      - label: "Configuración"
        key: "s"
        action: "submenu"
        target: "menu_config"

  menu_bitacoras:
    title: "G E S T I Ó N  D E  B I T Á C O R A S"
    items:
      - label: "Nueva Entrada"
        key: "n"
        action: "exec"
        command: "scripts.logs.new_entry"
        context_tag: "active_vault"
      - label: "Volver"
        key: "v"
        action: "submenu"
        target: "principal"
```

**Atributo clave: `context_tag`**
- El motor de menú evaluará el estado del sistema (ej. `vault_active = True/False`).
- Si un ítem tiene un `context_tag` que no se cumple, el ítem se oculta o se deshabilita automáticamente.

---

## 2. Mapeo de "Aplanamiento" (Flattening)
Para reducir la fatiga de navegación, implementaremos un mapeo de accesos directos condicionales.

- **Nivel 0 (Fijo):** Salir, Ayuda, Configuración.
- **Nivel 1 (Dinámico):** Si el motor detecta que el usuario está dentro de una carpeta de Vault (`MyJobNotes` o `PersonalNotes`), el menú principal inyectará automáticamente las opciones de "Nueva Entrada" y "Consolidar" en la raíz.

---

## 3. Estándar de Quick-Keys
Para asegurar que los inputs sean rápidos y tolerantes (Mecanismo Quick-Key):

1. **Unicidad por Nivel:** Ninguna tecla se repite dentro del mismo menú.
2. **Mnémicos Consistentes:**
   - `b` siempre para Bitácoras.
   - `c` siempre para Consolidar/Configurar.
   - `q` o `x` siempre para Salir.
3. **Case Insensitive:** El motor aceptará tanto `B` como `b`.
4. **Validación Instantánea:** El input no requerirá `Enter` si la longitud del comando es 1 (usando `getch` o similar en la implementación final).

---

## 4. Comparativa de Clics (Navegación)

| Acción         | Flujo Actual (main.py hardcoded)    | Flujo Propuesto (Aplanamiento) | Mejora       |
| :------------- | :---------------------------------- | :----------------------------- | :----------- |
| Nueva Bitácora | `1` (Log) -> `1` (New) -> `Enter`   | `n` (Directo si hay vault)     | **-2 clics** |
| Consolidar     | `2` (Proc) -> `3` (Cons) -> `Enter` | `c` (Contextual)               | **-2 clics** |
| Cambiar Vault  | `4` (Set) -> `2` (Path) -> `Input`  | `v` (Vanguardia de estado)     | **Agilidad** |

---

### Siguientes Pasos para el Developer:
1. **Extracción:** Mover la lógica de `if/elif` de `main.py` hacia un `MenuEngine`.
2. **Implementación de Contexto:** Crear un decorador o check de estado que valide los `context_tag`.
3. **Carga Lazy:** Cargar el YAML solo al inicio o bajo demanda para mantener la velocidad.

---

## Estado de Implementación (2026-05-24)

- ✅ Se creó el motor desacoplado de menú: `brackets/core/menu_engine.py`.
- ✅ Se creó y extendió la configuración YAML: `data/menu_config.yaml`.
- ✅ Se desacoplaron menú principal y submenús (generación, consolidación, archivos, herramientas, listado y configuración).
- ✅ Se activó resolución de quick-keys por YAML con validación de conflictos de teclas visibles.
- ✅ Se implementó navegación de menú por tecla única (sin Enter) para reducir fricción diaria.
