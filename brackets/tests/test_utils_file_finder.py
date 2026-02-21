#!/usr/bin/env python3
"""
Tests unitarios para FileFinder en utils/file_finder.py
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from brackets.utils.file_finder import FileFinder


class TestFileFinder:
    """Tests para la clase FileFinder."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
    
    def test_extract_week_info(self):
        """Test que _extract_week_info parsea correctamente."""
        try:
            finder = FileFinder(".")
            filepath = "/path/to/[2026][01]Week05.md"
            
            info = finder._extract_week_info(filepath)
            
            assert info is not None, "No debería retornar None"
            path, year, month, week = info
            assert year == 2026, f"Año incorrecto: {year}"
            assert month == 1, f"Mes incorrecto: {month}"
            assert week == 5, f"Semana incorrecta: {week}"
            
            print("✅ Test: _extract_week_info parsea correctamente")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test _extract_week_info falló: {e}")
            self.failed += 1
    
    def test_extract_month_info(self):
        """Test que _extract_month_info parsea correctamente."""
        try:
            finder = FileFinder(".")
            filepath = "/path/to/[2026][01]MonthTopics.md"
            
            info = finder._extract_month_info(filepath)
            
            assert info is not None, "No debería retornar None"
            path, year, month = info
            assert year == 2026, f"Año incorrecto: {year}"
            assert month == 1, f"Mes incorrecto: {month}"
            
            print("✅ Test: _extract_month_info parsea correctamente")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test _extract_month_info falló: {e}")
            self.failed += 1
    
    def test_list_weekly_files_empty(self):
        """Test que list_weekly_files retorna lista vacía si no hay archivos."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                finder = FileFinder(tmpdir)
                files = finder.list_weekly_files()
                
                assert isinstance(files, list), "Debería retornar lista"
                assert len(files) == 0, "No debería haber archivos"
                
                print("✅ Test: list_weekly_files retorna lista vacía correctamente")
                self.passed += 1
        except Exception as e:
            print(f"❌ Test list_weekly_files_empty falló: {e}")
            self.failed += 1
    
    def test_list_monthly_files_empty(self):
        """Test que list_monthly_files retorna lista vacía si no hay archivos."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                finder = FileFinder(tmpdir)
                files = finder.list_monthly_files()
                
                assert isinstance(files, list), "Debería retornar lista"
                assert len(files) == 0, "No debería haber archivos"
                
                print("✅ Test: list_monthly_files retorna lista vacía correctamente")
                self.passed += 1
        except Exception as e:
            print(f"❌ Test list_monthly_files_empty falló: {e}")
            self.failed += 1
    
    def test_get_most_recent_weekly_empty(self):
        """Test que get_most_recent_weekly retorna None si no hay archivos."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                finder = FileFinder(tmpdir)
                recent = finder.get_most_recent_weekly()
                
                assert recent is None, "Debería retornar None si no hay archivos"
                
                print("✅ Test: get_most_recent_weekly retorna None correctamente")
                self.passed += 1
        except Exception as e:
            print(f"❌ Test get_most_recent_weekly_empty falló: {e}")
            self.failed += 1
    
    def test_pattern_matching(self):
        """Test que los patrones de regex funcionan correctamente."""
        try:
            finder = FileFinder(".")
            
            # Nombres válidos
            valid_weekly = "[2026][01]Week05.md"
            valid_monthly = "[2026][01]MonthTopics.md"
            
            # Nombres inválidos
            invalid_weekly = "[2026]01Week05.md"  # Falta corchete
            invalid_monthly = "[2026][01]Topics.md"  # Falta MonthTopics
            
            # Los inválidos deberían retornar None
            assert finder._extract_week_info(invalid_weekly) is None
            assert finder._extract_month_info(invalid_monthly) is None
            
            print("✅ Test: Patrones regex funcionan correctamente")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test pattern_matching falló: {e}")
            self.failed += 1
    
    def run_all(self):
        """Ejecutar todos los tests."""
        print("\n🧪 TESTS: utils/file_finder.py")
        print("=" * 50)
        
        self.test_extract_week_info()
        self.test_extract_month_info()
        self.test_list_weekly_files_empty()
        self.test_list_monthly_files_empty()
        self.test_get_most_recent_weekly_empty()
        self.test_pattern_matching()
        
        print(f"\n📊 Resultado: ✅ {self.passed} | ❌ {self.failed}")
        return self.failed == 0


if __name__ == "__main__":
    tester = TestFileFinder()
    success = tester.run_all()
    sys.exit(0 if success else 1)
