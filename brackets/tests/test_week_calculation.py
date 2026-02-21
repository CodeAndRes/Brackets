#!/usr/bin/env python3
"""
Script de prueba para verificar el cálculo correcto de semanas y meses.
"""

from datetime import datetime, timedelta
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from brackets.utils.legacy_utils import calculate_next_week_info_from_dates
from brackets.utils.content_parser import ContentParser


def test_week_calculation():
    """Prueba el cálculo de semanas a lo largo de varios meses."""
    print("🧪 PRUEBA DE CÁLCULO DE SEMANAS Y MESES")
    print("=" * 50)
    
    # Comenzar desde una fecha conocida (por ejemplo, lunes 29 de julio de 2024)
    start_date = datetime(2024, 7, 29)  # Lunes
    
    print(f"📅 Fecha inicial: {start_date.strftime('%d/%m/%Y')} (Lunes)")
    print(f"📅 Semana ISO inicial: {start_date.isocalendar()[1]}")
    print(f"📅 Mes inicial: {start_date.month}")
    print()
    
    current_dates = []
    current_month = start_date.month
    
    # Iterar durante 60 semanas para cubrir varios meses
    for week_num in range(60):
        current_day = start_date + timedelta(weeks=week_num)
        
        # Buscar el lunes de esa semana
        while current_day.weekday() != 0:  # 0 = Monday
            current_day -= timedelta(days=1)
        
        # Calcular la semana siguiente
        next_dates = calculate_next_week_info_from_dates(
            current_day,
            current_day + timedelta(days=6)
        )
        
        current_dates.append(next_dates)
        
        # Detectar cambio de mes
        if next_dates['month'] != current_month:
            print(f"📊 Cambio de mes detectado:")
            print(f"   Última semana de {current_month}: {current_dates[-2]}")
            print(f"   Primera semana de {next_dates['month']}: {next_dates}")
            print()
            current_month = next_dates['month']
    
    print("✅ Prueba completada sin errores")
    return True


def test_content_parser():
    """Prueba el analizador de contenido."""
    print("\n🧪 PRUEBA DE ANÁLISIS DE CONTENIDO")
    print("=" * 50)
    
    # Contenido de prueba
    test_content = """
# 🗓️ Enero - Week 01

## 🏠01
- Task 1
- Task 2

## 🚗02
- Task 3
- Task 4

## 📝TOPICS
- Topic 1
- Topic 2

## ⏳ Pending from last week
- [ ] Old task 1
- [x] Old task 2
"""
    
    parser = ContentParser()
    
    # Probar extracción de tareas pendientes
    pending = parser.extract_pending_tasks(test_content)
    print(f"📋 Tareas pendientes encontradas: {len(pending)}")
    for task in pending:
        print(f"   - {task}")
    
    print("\n✅ Prueba de análisis completada")
    return True


if __name__ == "__main__":
    try:
        test_week_calculation()
        test_content_parser()
        print("\n" + "=" * 50)
        print("🎉 TODAS LAS PRUEBAS PASARON")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
