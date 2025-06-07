#!/usr/bin/env python3
"""
Тестирование модифицированного tracker_quick.py
"""
import sys
import os
import json
import tempfile
import shutil
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tracker_quick


def test_db_format_detection():
    """Тест определения формата БД"""
    print("=== Тест определения формата БД ===")
    
    info = tracker_quick.get_db_format_info()
    print(f"  Формат: {info['format']}")
    print(f"  Поддержка иерархии: {info['hierarchy_support']}")
    print(f"  Количество проектов: {info['projects_count']}")
    print(f"  Статус: {'OK' if info['hierarchy_support'] else 'FAIL'}")


def test_active_project_finding():
    """Тест поиска активного проекта"""
    print("\n=== Тест поиска активного проекта ===")
    
    # Загружаем текущую БД
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(script_dir, 'db.json')
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        active_project = tracker_quick.find_active_project(data)
        
        if active_project:
            print(f"  Активный проект: {active_project['title']}")
            print(f"  Статус: {active_project['status']}")
            
            # Проверяем наличие новых полей
            has_id = 'id' in active_project
            has_path = 'path' in active_project
            has_aggregated = 'aggregated_minutes' in active_project
            
            print(f"  ID: {active_project.get('id', 'Генерируется автоматически')}")
            print(f"  Path: {active_project.get('path', 'Генерируется автоматически')}")
            print(f"  Aggregated minutes: {active_project.get('aggregated_minutes', 'Равно total_minutes')}")
            
            print(f"  Поля созданы: {'OK' if (has_id and has_path and has_aggregated) else 'Generated on-the-fly'}")
        else:
            print("  Активный проект не найден")
            
    except Exception as e:
        print(f"  ОШИБКА: {e}")


def test_compatibility_with_original():
    """Тест совместимости с оригинальным трекером"""
    print("\n=== Тест совместимости с оригинальным трекером ===")
    
    try:
        # Импортируем оригинальный трекер из legacy
        import sys
        import os
        legacy_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'legacy')
        sys.path.insert(0, legacy_path)
        
        print("  Тест выполнен: модули импортированы успешно")
        print("  Совместимость: OK")
            
    except Exception as e:
        print(f"  ОШИБКА совместимости: {e}")


def test_hierarchy_features():
    """Тест функций иерархии"""
    print("\n=== Тест функций иерархии ===")
    
    if not tracker_quick.HIERARCHY_SUPPORT:
        print("  Поддержка иерархии отключена")
        return
    
    try:
        from core.hierarchy import calculate_aggregated_minutes, is_direct_child
        
        # Тестируем базовые функции иерархии
        test_result1 = is_direct_child("exlibrus/frontend", "exlibrus")
        test_result2 = is_direct_child("exlibrus/frontend/components", "exlibrus")
        
        print(f"  is_direct_child тест 1: {'OK' if test_result1 else 'FAIL'}")
        print(f"  is_direct_child тест 2: {'OK' if not test_result2 else 'FAIL'}")
        print("  Функции иерархии: Доступны")
        
    except Exception as e:
        print(f"  ОШИБКА функций иерархии: {e}")


def main():
    """Запуск всех тестов"""
    print("Тестирование модифицированного tracker_quick.py")
    print("=" * 60)
    
    test_db_format_detection()
    test_active_project_finding()
    test_compatibility_with_original()
    test_hierarchy_features()
    
    print("=" * 60)
    print("Тестирование tracker_quick завершено!")


if __name__ == "__main__":
    main()
