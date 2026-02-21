#!/usr/bin/env python3
"""
Runner para ejecutar todos los tests unitarios del sistema Brackets.
Ejecutar desde la raíz del proyecto: python -m brackets.tests.test_suite
"""

import sys
import os

# Agregar el directorio raíz al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importar todos los tests
from brackets.tests.test_consolidators import test_imports, test_month_consolidator_init
from brackets.tests.test_consolidators import test_year_consolidator_init, test_season_emoji
from brackets.tests.test_consolidators import test_list_available_months, test_list_available_years
from brackets.tests.test_utils_helpers import TestHelpers
from brackets.tests.test_utils_markdown import TestMarkdown
from brackets.tests.test_utils_legacy import TestLegacyUtils
from brackets.tests.test_utils_content_parser import TestContentParser
from brackets.tests.test_utils_content_generator import TestContentGenerator
from brackets.tests.test_utils_file_finder import TestFileFinder


def run_all_tests():
    """Ejecutar todos los tests y mostrar resumen."""
    print("\n" + "=" * 60)
    print("🚀 EJECUTANDO SUITE COMPLETA DE TESTS UNITARIOS")
    print("=" * 60)
    
    total_passed = 0
    total_failed = 0
    
    # Tests de consolidadores (existentes)
    print("\n" + "=" * 60)
    print("🧪 MÓDULO: Consolidadores")
    print("=" * 60)
    
    consolidator_tests = [
        ("Importaciones", test_imports),
        ("MonthConsolidator init", test_month_consolidator_init),
        ("YearConsolidator init", test_year_consolidator_init),
        ("Season emoji", test_season_emoji),
        ("List available months", test_list_available_months),
        ("List available years", test_list_available_years),
    ]
    
    for test_name, test_func in consolidator_tests:
        try:
            result = test_func()
            if result:
                total_passed += 1
            else:
                total_failed += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            total_failed += 1
    
    # Tests de helpers
    tester = TestHelpers()
    helpers_passed = tester.run_all()
    total_passed += tester.passed
    total_failed += tester.failed
    
    # Tests de markdown
    tester = TestMarkdown()
    markdown_passed = tester.run_all()
    total_passed += tester.passed
    total_failed += tester.failed
    
    # Tests de legacy_utils
    tester = TestLegacyUtils()
    legacy_passed = tester.run_all()
    total_passed += tester.passed
    total_failed += tester.failed
    
    # Tests de content_parser
    tester = TestContentParser()
    parser_passed = tester.run_all()
    total_passed += tester.passed
    total_failed += tester.failed
    
    # Tests de content_generator
    tester = TestContentGenerator()
    generator_passed = tester.run_all()
    total_passed += tester.passed
    total_failed += tester.failed
    
    # Tests de file_finder
    tester = TestFileFinder()
    finder_passed = tester.run_all()
    total_passed += tester.passed
    total_failed += tester.failed
    
    # Mostrar resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL DE TESTS")
    print("=" * 60)
    print(f"✅ Tests pasados: {total_passed}")
    print(f"❌ Tests fallidos: {total_failed}")
    print(f"📈 Total: {total_passed + total_failed}")
    
    if total_failed == 0:
        percentage = 100
        status = "🎉 TODOS LOS TESTS PASARON"
    else:
        percentage = (total_passed / (total_passed + total_failed)) * 100
        status = f"⚠️  {percentage:.1f}% de tests pasaron"
    
    print(f"📊 Cobertura: {percentage:.1f}%")
    print(status)
    print("=" * 60 + "\n")
    
    return total_failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
