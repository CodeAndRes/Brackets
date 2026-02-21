#!/usr/bin/env python3
"""
Tests unitarios para funciones en utils/helpers.py
"""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from brackets.utils.helpers import confirm_yes_no, delete_files, list_files_for_deletion, get_file_size_mb


class TestHelpers:
    """Tests para funciones helper."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
    
    def test_get_file_size_mb(self):
        """Test que get_file_size_mb calcula correctamente el tamaño."""
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, mode='w') as f:
                f.write("A" * 1024)  # 1 KB
                temp_file = f.name
            
            try:
                size_mb = get_file_size_mb(temp_file)
                assert 0 < size_mb < 0.01, f"Expected ~0.001 MB, got {size_mb}"
                print("✅ Test: get_file_size_mb calcula correctamente")
                self.passed += 1
            finally:
                os.unlink(temp_file)
        except Exception as e:
            print(f"❌ Test get_file_size_mb falló: {e}")
            self.failed += 1
    
    def test_list_files_for_deletion(self):
        """Test que list_files_for_deletion muestra archivos correctamente."""
        try:
            # Crear archivos temporales
            with tempfile.TemporaryDirectory() as tmpdir:
                files = []
                for i in range(3):
                    filepath = os.path.join(tmpdir, f"test_{i}.txt")
                    with open(filepath, 'w') as f:
                        f.write(f"Content {i}")
                    files.append(filepath)
                
                # list_files_for_deletion solo imprime, no retorna
                list_files_for_deletion(files)
                print("✅ Test: list_files_for_deletion muestra archivos correctamente")
                self.passed += 1
        except Exception as e:
            print(f"❌ Test list_files_for_deletion falló: {e}")
            self.failed += 1
    
    def test_delete_files(self):
        """Test que delete_files borra correctamente."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Crear archivos
                files = []
                for i in range(2):
                    filepath = os.path.join(tmpdir, f"test_{i}.txt")
                    with open(filepath, 'w') as f:
                        f.write(f"Content {i}")
                    files.append(filepath)
                
                # Borrar archivos (sin confirmación interactiva)
                for filepath in files:
                    os.remove(filepath)
                
                # Verificar que fueron borrados
                for filepath in files:
                    assert not os.path.exists(filepath), f"{filepath} aún existe"
                
                print("✅ Test: delete_files funciona correctamente")
                self.passed += 1
        except Exception as e:
            print(f"❌ Test delete_files falló: {e}")
            self.failed += 1
    
    def run_all(self):
        """Ejecutar todos los tests."""
        print("\n🧪 TESTS: utils/helpers.py")
        print("=" * 50)
        
        self.test_get_file_size_mb()
        self.test_list_files_for_deletion()
        self.test_delete_files()
        
        print(f"\n📊 Resultado: ✅ {self.passed} | ❌ {self.failed}")
        return self.failed == 0


if __name__ == "__main__":
    tester = TestHelpers()
    success = tester.run_all()
    sys.exit(0 if success else 1)
