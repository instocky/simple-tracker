#!/usr/bin/env python3
"""
Тестирование модулей core
"""
import sys
import os

# Добавляем путь к проекту для импорта (поднимаемся на уровень выше)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.transliteration import transliterate, generate_id_from_title, validate_path
from core.compatibility import detect_db_format, ensure_project_fields
from core.hierarchy import calculate_aggregated_minutes, is_direct_child, get_all_parent_paths


def test_transliteration():
    """Тест модуля транслитерации"""
    print("=== Тест транслитерации ===")
    
    test_cases = [
        ("ExLibrus", "exlibrus"),
        ("Б24 Отчеты", "b24-otchety"), 
        ("React Components", "react-components"),
        ("API интеграция v2.0", "api-integratsiya-v2-0")
    ]
    
    for input_text, expected in test_cases:
        result = transliterate(input_text)
        status = "OK" if result == expected else "FAIL"
        print(f"  {input_text} -> {result} [{status}]")
        if result != expected:
            print(f"    Ожидался: {expected}")


def test_compatibility():
    """Тест модуля совместимости"""
    print("\n=== Тест совместимости ===")
    
    # Старый формат
    old_data = {
        "projects": [
            {
                "title": "exlibrus",
                "status": "active", 
                "total_minutes": 335
            }
        ]
    }
    
    # Новый формат
    new_data = {
        "projects": [
            {
                "id": "exlibrus",
                "path": "exlibrus",
                "title": "ExLibrus",
                "status": "active",
                "total_minutes": 335,
                "aggregated_minutes": 335
            }
        ]
    }
    
    old_format = detect_db_format(old_data)
    new_format = detect_db_format(new_data)
    
    print(f"  Старый формат: {old_format} [{'OK' if old_format == 'old' else 'FAIL'}]")
    print(f"  Новый формат: {new_format} [{'OK' if new_format == 'new' else 'FAIL'}]")
    
    # Тест добавления полей
    old_project = old_data['projects'][0].copy()
    enhanced = ensure_project_fields(old_project)
    
    has_all_fields = all(field in enhanced for field in ['id', 'path', 'aggregated_minutes'])
    print(f"  Генерация полей: {'OK' if has_all_fields else 'FAIL'}")
    if has_all_fields:
        print(f"    id: {enhanced['id']}")
        print(f"    path: {enhanced['path']}")


def test_hierarchy():
    """Тест модуля иерархии"""
    print("\n=== Тест иерархии ===")
    
    # Тестовые проекты
    projects = [
        {
            'id': 'exlibrus',
            'path': 'exlibrus',
            'title': 'ExLibrus',
            'total_minutes': 50
        },
        {
            'id': 'exlibrus-frontend',
            'path': 'exlibrus/frontend',
            'title': 'Frontend',
            'total_minutes': 120
        },
        {
            'id': 'exlibrus-frontend-components',
            'path': 'exlibrus/frontend/components',
            'title': 'Components',
            'total_minutes': 60
        }
    ]
    
    # Тест прямых детей
    is_child1 = is_direct_child("exlibrus/frontend", "exlibrus")
    is_child2 = is_direct_child("exlibrus/frontend/components", "exlibrus")
    
    print(f"  exlibrus/frontend - прямой ребенок exlibrus: {is_child1} [{'OK' if is_child1 else 'FAIL'}]")
    print(f"  exlibrus/frontend/components - НЕ прямой ребенок exlibrus: {not is_child2} [{'OK' if not is_child2 else 'FAIL'}]")
    
    # Тест родительских путей
    parents = get_all_parent_paths("exlibrus/frontend/components")
    expected_parents = ["exlibrus/frontend", "exlibrus"]
    parents_ok = parents == expected_parents
    
    print(f"  Родители для exlibrus/frontend/components: {parents} [{'OK' if parents_ok else 'FAIL'}]")
    
    # Тест расчета aggregated_minutes
    for project in projects:
        path = project['path']
        aggregated = calculate_aggregated_minutes(path, projects)
        print(f"  {path}: {project['total_minutes']} собственных -> {aggregated} общих")


def main():
    """Запуск всех тестов"""
    print("Тестирование модулей core/")
    print("=" * 50)
    
    try:
        test_transliteration()
        test_compatibility()
        test_hierarchy()
        
        print("\n" + "=" * 50)
        print("Все тесты завершены!")
        
    except Exception as e:
        print(f"\nОШИБКА в тестах: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
