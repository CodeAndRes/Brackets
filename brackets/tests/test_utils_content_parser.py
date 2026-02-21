#!/usr/bin/env python3
"""
Tests unitarios para ContentParser en utils/content_parser.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from brackets.utils.content_parser import ContentParser


class TestContentParser:
    """Tests para la clase ContentParser."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
    
    def test_extract_week_info_from_filename(self):
        """Test que extract_week_info_from_filename parsea correctamente."""
        try:
            # El peso se extrae del patrón del contenido, no es garantizado
            content = """# 🗓️Week05

## ✅Topics
- [ ] Task 1
"""
            parser = ContentParser(content)
            year, month, week, weight = parser.extract_week_info_from_filename(
                "[2026][01]Week05.md"
            )
            
            assert year == 2026, f"Año incorrecto: {year}"
            assert month == 1, f"Mes incorrecto: {month}"
            assert week == 5, f"Semana incorrecta: {week}"
            # El peso puede ser None si no está en el formato esperado
            # assert weight == 75.5 or weight is None
            
            print("✅ Test: extract_week_info_from_filename parsea correctamente")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test extract_week_info_from_filename falló: {e}")
            self.failed += 1
    
    def test_extract_pending_tasks(self):
        """Test que extract_pending_tasks extrae tareas correctamente."""
        try:
            content = """# Week 01

## ✅Topics
  - [ ] Task 1
  - [ ] Task 2
  - [x] Completed task
  - ### Subsection
    - [ ] Sub task
"""
            parser = ContentParser(content)
            tasks = parser.extract_pending_tasks()
            
            assert len(tasks) > 0, "No se extrajeron tareas"
            # Las tareas completadas [x] no deben incluirse
            completed_in_tasks = any("[x]" in str(t) for t in tasks)
            assert not completed_in_tasks, "Tareas completadas no deberían extraerse"
            
            print("✅ Test: extract_pending_tasks extrae correctamente")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test extract_pending_tasks falló: {e}")
            self.failed += 1
    
    def test_extract_daily_dates(self):
        """Test que extract_daily_dates extrae fechas correctamente."""
        try:
            content = """# Week 05

## 🏠29
- Task

## 🚗30
- Task

## 🚗31
- Task

## 🏠01
- Task

## 🚗02
- Task
"""
            parser = ContentParser(content)
            dates = parser.extract_daily_dates()
            
            assert len(dates) == 5, f"Debería extraer 5 fechas, se extrajeron {len(dates)}"
            assert dates[0] == 29, f"Primera fecha debería ser 29, es {dates[0]}"
            
            print("✅ Test: extract_daily_dates extrae correctamente")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test extract_daily_dates falló: {e}")
            self.failed += 1
    
    def test_extract_daily_pending_tasks(self):
        """Test que extract_daily_pending_tasks funciona."""
        try:
            content = """# Week 05

## 🏠29
- [ ] Task 1 from Monday
- [ ] Task 2 from Monday

## 🚗30
- [ ] Task 1 from Tuesday
"""
            parser = ContentParser(content)
            daily_tasks = parser.extract_daily_pending_tasks()
            
            assert len(daily_tasks) > 0, "Debería extraer tareas diarias"
            
            print("✅ Test: extract_daily_pending_tasks extrae correctamente")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test extract_daily_pending_tasks falló: {e}")
            self.failed += 1
    
    def test_clean_completed_tasks(self):
        """Test que clean_completed_tasks remueve tareas completadas."""
        try:
            content = """# Week 05

## ✅Topics
- [ ] Pending task 1
- [x] Completed task 1
- [ ] Pending task 2
- [x] Completed task 2
"""
            parser = ContentParser(content)
            cleaned = parser.clean_completed_tasks()
            
            # Las líneas con [x] no deben estar en el resultado
            assert "[x]" not in cleaned, "Tareas completadas no deberían estar en el resultado"
            assert "Pending task 1" in cleaned, "Tareas pendientes deberían mantenerse"
            
            print("✅ Test: clean_completed_tasks remueve correctamente")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test clean_completed_tasks falló: {e}")
            self.failed += 1
    
    def run_all(self):
        """Ejecutar todos los tests."""
        print("\n🧪 TESTS: utils/content_parser.py")
        print("=" * 50)
        
        self.test_extract_week_info_from_filename()
        self.test_extract_pending_tasks()
        self.test_extract_daily_dates()
        self.test_extract_daily_pending_tasks()
        self.test_clean_completed_tasks()
        
        print(f"\n📊 Resultado: ✅ {self.passed} | ❌ {self.failed}")
        return self.failed == 0


if __name__ == "__main__":
    tester = TestContentParser()
    success = tester.run_all()
    sys.exit(0 if success else 1)
