#!/usr/bin/env python3
"""
Script de prueba para la creación manual de bitácoras.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brackets.generators.weekly import WeeklyGenerator
from brackets.utils.content_generator import ContentGenerator

def test_manual_bitacora_generation():
    """Prueba la generación manual de una bitácora."""
    print("🧪 PRUEBA: Generación Manual de Bitácora")
    print("=" * 50)
    
    # Crear generador de contenido
    generator = ContentGenerator()
    
    # Parámetros de prueba
    year = 2025
    month = 1
    week = 1
    weight = 75.5
    
    # Ubicaciones de trabajo personalizadas
    work_locations = {
        29: "🏠",  # Lunes - Casa
        30: "🚗",  # Martes - Oficina
        31: "🚗",  # Miércoles - Oficina
        1: "🏠",   # Jueves - Casa
        2: "🚗"    # Viernes - Oficina
    }
    
    print(f"\n📊 Parámetros:")
    print(f"  Año: {year}")
    print(f"  Mes: {month}")
    print(f"  Semana: {week}")
    print(f"  Peso: {weight}")
    print(f"  Ubicaciones: {work_locations}")
    
    # Generar contenido
    content = generator.generate_weekly_content_manual(
        year=year,
        month=month,
        week=week,
        weight=weight,
        work_locations=work_locations
    )
    
    if content:
        print("\n✅ Contenido generado exitosamente:")
        print("-" * 50)
        print(content)
        print("-" * 50)
        return True
    else:
        print("\n❌ Error generando contenido")
        return False


def test_manual_weekly_creation():
    """Prueba la creación manual de bitácora en el generador."""
    print("\n🧪 PRUEBA: Creación Manual en WeeklyGenerator")
    print("=" * 50)
    
    # Crear generador
    generator = WeeklyGenerator(directory=".")
    
    # Verificar que el método existe
    if hasattr(generator, 'create_manual_weekly_bitacora'):
        print("✅ Método create_manual_weekly_bitacora existe")
        return True
    else:
        print("❌ Método create_manual_weekly_bitacora NO existe")
        return False


if __name__ == "__main__":
    print("\n🚀 EJECUTANDO PRUEBAS DE CREACIÓN MANUAL\n")
    
    result1 = test_manual_bitacora_generation()
    result2 = test_manual_weekly_creation()
    
    print("\n" + "=" * 50)
    if result1 and result2:
        print("✅ TODAS LAS PRUEBAS PASARON")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
    print("=" * 50)
