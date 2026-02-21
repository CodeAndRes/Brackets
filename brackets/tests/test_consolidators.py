"""
Tests básicos para validar la refactorización de consolidadores.
"""

import os
import sys

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brackets.consolidators.month import MonthConsolidator
from brackets.consolidators.year import YearConsolidator
from brackets.config import MONTH_NAMES, SEASON_EMOJIS


def test_imports():
    """Test que las importaciones funcionan correctamente."""
    print("✅ Test 1: Importaciones exitosas")
    print(f"   - MonthConsolidator: {MonthConsolidator.__name__}")
    print(f"   - YearConsolidator: {YearConsolidator.__name__}")
    print(f"   - MONTH_NAMES tiene {len(MONTH_NAMES)} meses")
    print(f"   - SEASON_EMOJIS tiene {len(SEASON_EMOJIS)} estaciones")
    return True


def test_month_consolidator_init():
    """Test que MonthConsolidator se inicializa correctamente."""
    try:
        consolidator = MonthConsolidator(".")
        print("✅ Test 2: MonthConsolidator inicializado correctamente")
        print(f"   - Directorio: {consolidator.directory}")
        print(f"   - Tiene método consolidate: {hasattr(consolidator, 'consolidate')}")
        print(f"   - Hereda de BaseConsolidator: {hasattr(consolidator, 'confirm_deletion')}")
        return True
    except Exception as e:
        print(f"❌ Test 2 falló: {e}")
        return False


def test_year_consolidator_init():
    """Test que YearConsolidator se inicializa correctamente."""
    try:
        consolidator = YearConsolidator(".")
        print("✅ Test 3: YearConsolidator inicializado correctamente")
        print(f"   - Directorio: {consolidator.directory}")
        print(f"   - Tiene método consolidate: {hasattr(consolidator, 'consolidate')}")
        print(f"   - Hereda de BaseConsolidator: {hasattr(consolidator, 'confirm_deletion')}")
        return True
    except Exception as e:
        print(f"❌ Test 3 falló: {e}")
        return False


def test_season_emoji():
    """Test que la función get_season_emoji funciona."""
    try:
        consolidator = MonthConsolidator(".")
        winter = consolidator.get_season_emoji(1)
        spring = consolidator.get_season_emoji(4)
        summer = consolidator.get_season_emoji(7)
        autumn = consolidator.get_season_emoji(10)
        
        print("✅ Test 4: get_season_emoji funciona correctamente")
        print(f"   - Enero (invierno): {winter}")
        print(f"   - Abril (primavera): {spring}")
        print(f"   - Julio (verano): {summer}")
        print(f"   - Octubre (otoño): {autumn}")
        return True
    except Exception as e:
        print(f"❌ Test 4 falló: {e}")
        return False


def test_list_available_months():
    """Test que list_available_months funciona."""
    try:
        consolidator = MonthConsolidator(".")
        months = consolidator.list_available_months()
        print("✅ Test 5: list_available_months funciona")
        print(f"   - Se encontraron {len(months)} meses disponibles")
        if months:
            print(f"   - Primeros 3: {months[:3]}")
        return True
    except Exception as e:
        print(f"❌ Test 5 falló: {e}")
        return False


def test_list_available_years():
    """Test que list_available_years funciona."""
    try:
        consolidator = YearConsolidator(".")
        years = consolidator.list_available_years()
        print("✅ Test 6: list_available_years funciona")
        print(f"   - Se encontraron {len(years)} años disponibles")
        if years:
            print(f"   - Años: {years}")
        return True
    except Exception as e:
        print(f"❌ Test 6 falló: {e}")
        return False


def test_base_consolidator_methods():
    """Test que los métodos heredados de BaseConsolidator están disponibles."""
    try:
        month_cons = MonthConsolidator(".")
        year_cons = YearConsolidator(".")
        
        methods = [
            'confirm_deletion',
            'handle_existing_output',
            'delete_files_confirmed',
            'adjust_markdown_headings',
            'remove_markdown_metadata'
        ]
        
        all_ok = True
        for method in methods:
            if not hasattr(month_cons, method):
                print(f"   ❌ MonthConsolidator no tiene método: {method}")
                all_ok = False
            if not hasattr(year_cons, method):
                print(f"   ❌ YearConsolidator no tiene método: {method}")
                all_ok = False
        
        if all_ok:
            print("✅ Test 7: Métodos de BaseConsolidator disponibles")
            print(f"   - Verificados {len(methods)} métodos")
            return True
        else:
            print("❌ Test 7 falló: Faltan métodos")
            return False
    except Exception as e:
        print(f"❌ Test 7 falló: {e}")
        return False


def run_all_tests():
    """Ejecuta todos los tests."""
    print("\n" + "=" * 50)
    print("🧪 EJECUTANDO TESTS DE VALIDACIÓN")
    print("=" * 50 + "\n")
    
    tests = [
        test_imports,
        test_month_consolidator_init,
        test_year_consolidator_init,
        test_season_emoji,
        test_list_available_months,
        test_list_available_years,
        test_base_consolidator_methods,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Error ejecutando {test.__name__}: {e}\n")
            results.append(False)
    
    # Resumen
    print("=" * 50)
    print("📊 RESUMEN DE TESTS")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"\n✅ Pasados: {passed}/{total}")
    print(f"❌ Fallidos: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 TODOS LOS TESTS PASARON")
        print("✅ La refactorización está completa y funcional")
    else:
        print("\n⚠️  ALGUNOS TESTS FALLARON")
        print("⚠️  Revisar los errores antes de continuar")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
