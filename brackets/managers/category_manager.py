"""
Gestor de categorías para Brackets.
Permite navegar, seleccionar y crear nuevas categorías/subcategorías.
"""

import os
import json
from typing import Optional, List, Dict, Any

# Lazy import - no cargar yaml al importar el módulo
yaml = None


class CategoryManager:
    """Gestor de categorías de documentos."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = os.path.abspath(data_dir)
        self.notes_root = os.path.dirname(self.data_dir)
        self.categories_file = os.path.join(self.data_dir, "categories.yaml")
        self.categories_data = self._load_categories()
    
    def _ensure_yaml(self):
        """Asegura que YAML esté disponible (lazy import)."""
        global yaml
        if yaml is None:
            try:
                import yaml as yaml_module
                yaml = yaml_module
            except ImportError:
                raise ImportError(
                    "Se requiere PyYAML. Instala con: python -m pip install pyyaml"
                )
    
    def _load_categories(self) -> Dict[str, Any]:
        """Carga la estructura de categorías desde YAML."""
        if not os.path.exists(self.categories_file):
            return {"categories": []}
        
        try:
            self._ensure_yaml()
            with open(self.categories_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if data else {"categories": []}
        except Exception as e:
            print(f"⚠️ Error cargando categorías: {e}")
            return {"categories": []}
    
    def _save_categories(self) -> bool:
        """Guarda la estructura de categorías a YAML."""
        try:
            self._ensure_yaml()
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.categories_file, "w", encoding="utf-8") as f:
                yaml.dump(self.categories_data, f, allow_unicode=True, sort_keys=False)
            return True
        except Exception as e:
            print(f"❌ Error guardando categorías: {e}")
            return False
    
    def select_category(self) -> Optional[Dict[str, Any]]:
        """Muestra menú de categorías y retorna la seleccionada."""
        categories = self.categories_data.get("categories", [])
        
        if not categories:
            print("❌ No hay categorías disponibles")
            return None
        
        print("\n📂 SELECCIONA UNA CATEGORÍA:")
        print("=" * 40)
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat.get('name', 'Sin nombre')} - {cat.get('description', '')}")
        print(f"{len(categories) + 1}. ➕ Crear nueva categoría")
        print("0. ↩️ Volver")
        print("-" * 40)
        
        choice = input("Opción: ").strip()
        
        if choice == "0":
            return None
        
        if choice == str(len(categories) + 1):
            return self._create_new_category()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(categories):
                return categories[idx]
        except ValueError:
            pass
        
        print("❌ Opción inválida")
        return None
    
    def select_subcategory(self, category: Dict[str, Any]):
        """Muestra menú de subcategorías y retorna el camino completo [root, sub1, sub2, ..., target]."""
        subcategories = category.get("subcategories", [])
        
        print(f"\n📁 SUBCATEGORÍAS DE {category.get('name', 'N/A')}:")
        print("=" * 40)
        
        for i, subcat in enumerate(subcategories, 1):
            print(f"{i}. {subcat.get('name', 'Sin nombre')} - {subcat.get('description', '')}")
        print(f"{len(subcategories) + 1}. ➕ Crear nueva subcategoría")
        print(f"{len(subcategories) + 2}. 📄 Crear documento en este nivel")
        print("0. ↩️ Volver")
        print("-" * 40)
        
        choice = input("Opción: ").strip()
        
        if choice == "0":
            return None
        
        if choice == str(len(subcategories) + 1):
            new_sub = self._create_new_subcategory(category)
            if new_sub:
                return [category, new_sub]
            return None
        
        if choice == str(len(subcategories) + 2):
            # Crear documento en el nivel actual (categoría)
            return [category]
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(subcategories):
                # Navegar recursivamente a la subcategoría seleccionada
                selected = subcategories[idx]
                # Permitir seguir navegando o crear aquí
                # Pasar el camino parcial [category, selected]
                result = self._navigate_or_create(selected, path=[category, selected])
                return result
        except ValueError:
            pass
        
        print("❌ Opción inválida")
        return None
    
    def _navigate_or_create(self, category: Dict[str, Any], path: list = None):
        """Permite navegar más profundo o crear documento en el nivel actual.
        Retorna el camino completo [root, sub1, sub2, ..., target]."""
        if path is None:
            path = [category]
        
        while True:
            subcats = category.get("subcategories", [])
            
            print(f"\n🗂️ NIVEL: {category.get('name')}")
            print("=" * 40)
            if subcats:
                for i, sub in enumerate(subcats, 1):
                    print(f"{i}. 📂 {sub.get('name')}")
            print(f"{len(subcats) + 1}. ➕ Crear nueva subcategoría aquí")
            print(f"{len(subcats) + 2}. 📄 Crear documento aquí")
            print("0. ↩️ Volver")
            print("-" * 40)
            
            choice = input("Opción: ").strip()
            
            if choice == "0":
                return None
            
            if choice == str(len(subcats) + 1):
                new_sub = self._create_new_subcategory(category)
                if new_sub:
                    new_path = path + [new_sub]
                    result = self._navigate_or_create(new_sub, path=new_path)
                    if result:
                        return result
                continue
            
            if choice == str(len(subcats) + 2):
                # Retornar el camino completo hasta el nivel actual
                return path
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(subcats):
                    next_cat = subcats[idx]
                    new_path = path + [next_cat]
                    result = self._navigate_or_create(next_cat, path=new_path)
                    if result:
                        return result
            except ValueError:
                pass
            
            print("❌ Opción inválida")
    
    def _create_new_category(self) -> Optional[Dict[str, Any]]:
        """Crea una nueva categoría interactivamente."""
        print("\n➕ CREAR NUEVA CATEGORÍA")
        print("=" * 40)
        
        name = input("Nombre de la categoría (ej: 📚 REFERENCIAS): ").strip()
        if not name:
            print("❌ Nombre requerido")
            return None
        
        description = input("Descripción (opcional): ").strip()
        
        new_cat = {
            "id": name.lower().replace(" ", "_").replace("📚", "").replace("🎯", ""),
            "name": name,
            "description": description,
            "subcategories": []
        }
        
        self.categories_data["categories"].append(new_cat)
        if self._save_categories():
            print(f"✅ Categoría '{name}' creada")
            return new_cat
        else:
            print("❌ Error al guardar categoría")
            self.categories_data["categories"].pop()
            return None
    
    def _create_new_subcategory(self, category: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crea una nueva subcategoría dentro de una categoría."""
        print("\n➕ CREAR NUEVA SUBCATEGORÍA")
        print("=" * 40)
        
        name = input("Nombre de la subcategoría (ej: PYTHON): ").strip()
        if not name:
            print("❌ Nombre requerido")
            return None
        
        description = input("Descripción (opcional): ").strip()
        
        new_subcat = {
            "id": name.lower().replace(" ", "_"),
            "name": name,
            "description": description,
            "subcategories": [],  # Permitir subcategorías anidadas
            "documents": []
        }
        
        if "subcategories" not in category:
            category["subcategories"] = []
        
        category["subcategories"].append(new_subcat)
        if self._save_categories():
            print(f"✅ Subcategoría '{name}' creada en '{category['name']}'")
            return new_subcat
        else:
            print("❌ Error al guardar subcategoría")
            category["subcategories"].pop()
            return None
    
    def create_document(self, path: list) -> bool:
        """Crea un nuevo documento en la ruta especificada.
        
        Args:
            path: Lista de categorías [root, sub1, sub2, ..., target]
        """
        if not path:
            return False
        
        # El último elemento es donde creamos
        target_category = path[-1]
        # El primero (o los primeros si es multicapa) son para el nombre
        
        print("\n📄 CREAR NUEVO DOCUMENTO")
        print("=" * 40)
        print(f"Ruta: {' → '.join([cat.get('name', '?') for cat in path])}")
        print("-" * 40)
        
        doc_name = input("Nombre del documento (extensión opcional, default .md): ").strip()
        if not doc_name:
            print("❌ Nombre requerido")
            return False
        
        # Solo añadir .md si no tiene extensión
        if '.' not in doc_name:
            doc_name += ".md"
        
        # Construir filename con TODO el camino (excepto el último que es el target)
        # Formato: [Nivel1][Nivel2][Nivel3]Nombre.md
        path_names = [cat.get('name', '') for cat in path]
        filename = "".join([f"[{name}]" for name in path_names]) + doc_name
        
        filepath = os.path.join(self.notes_root, filename)
        filepath = os.path.normpath(filepath)
        
        # Verificar si ya existe
        if os.path.exists(filepath):
            print(f"⚠️ El archivo ya existe: {filename}")
            overwrite = input("¿Sobrescribir? (s/n): ").strip().lower()
            if overwrite != "s":
                return False
        
        # Crear archivo vacío o con contenido básico
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                # Solo crear header si es .md
                if doc_name.endswith(".md"):
                    f.write(f"# {doc_name[:-3]}\n\n")
                else:
                    f.write("")  # Archivo vacío para otras extensiones
            
            # Actualizar estructura de categorías
            if "documents" not in target_category:
                target_category["documents"] = []
            target_category["documents"].append(doc_name)
            
            if self._save_categories():
                print(f"✅ Documento creado: {filename}")
                return True
            else:
                print("❌ Error al guardar en categorías")
                # Eliminar el archivo creado
                os.remove(filepath)
                return False
        
        except Exception as e:
            print(f"❌ Error creando documento: {e}")
            return False
    
    def interactive_create_document(self) -> bool:
        """Flujo interactivo completo: categoría → subcategoría → documento."""
        category = self.select_category()
        if not category:
            return False
        
        # select_subcategory retorna el camino completo (lista) al nivel donde crear
        path = self.select_subcategory(category)
        if not path:
            return False
        
        # path es una lista: [raíz_category, subcategory1, subcategory2, ..., target]
        return self.create_document(path)
        
        return self.create_document(category, subcategory)
    
    def list_all_categories(self) -> None:
        """Lista todas las categorías y subcategorías."""
        categories = self.categories_data.get("categories", [])
        
        if not categories:
            print("❌ No hay categorías")
            return
        
        print("\n📚 ESTRUCTURA DE CATEGORÍAS")
        print("=" * 50)
        
        for cat in categories:
            print(f"\n{cat.get('name')} ({cat.get('id')})")
            print(f"  → {cat.get('description', 'Sin descripción')}")
            
            subcats = cat.get("subcategories", [])
            if subcats:
                for subcat in subcats:
                    print(f"  ├─ {subcat.get('name')} ({subcat.get('id')})")
                    doc_count = len(subcat.get("documents", []))
                    print(f"     └─ {doc_count} documento(s)")
            else:
                docs = cat.get("documents", [])
                if docs:
                    print(f"  └─ {len(docs)} documento(s)")
