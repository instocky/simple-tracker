#!/usr/bin/env python3
"""
Тесты для project_manager.py
Проверка новых команд и совместимости
"""
import sys
import os

# Добавляем путь к проекту для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_new_commands():
    """Тест новых CLI команд"""
    print("=== Тест новых команд project_manager ===")
    
    try:
        import project_manager
        
        # Проверяем что новые функции доступны
        has_info = hasattr(project_manager, 'show_db_info')
        has_tree = hasattr(project_manager, 'show_tree')
        has_migrate = hasattr(project_manager, 'migrate_to_new_format')
        has_create = hasattr(project_manager, 'create_project')
        has_universal_search = hasattr(project_manager, 'find_project_universal')
        
        print(f"  Команда info: {'✓' if has_info else '✗'}")
        print(f"  Команда tree: {'✓' if has_tree else '✗'}")
        print(f"  Команда migrate: {'✓' if has_migrate else '✗'}")
        print(f"  Команда create: {'✓' if has_create else '✗'}")
        print(f"  Универсальный поиск: {'✓' if has_universal_search else '✗'}")
        
        return has_info and has_tree and has_migrate and has_create
        
    except Exception as e:
        print(f"  Ошибка тестирования команд: {e}")
        return False


def test_hierarchy_display():
    """Тест отображения иерархии"""
    print("\n=== Тест отображения иерархии ===")
    
    try:
        import project_manager
        
        # Тестируем загрузку и отображение
        data, _ = project_manager.load_db()
        
        # Проверяем что есть проекты с иерархией
        hierarchical_projects = 0
        for project in data.get('projects', []):
            if 'path' in project and '/' in project['path']:
                hierarchical_projects += 1
        
        print(f"  Проектов с иерархией: {hierarchical_projects}")
        
        # Проверяем поддержку иерархии
        hierarchy_support = getattr(project_manager, 'HIERARCHY_SUPPORT', False)
        print(f"  Поддержка иерархии: {'Включена' if hierarchy_support else 'Отключена'}")
        
        # Проверяем функции отображения
        has_hierarchical_list = hasattr(project_manager, 'list_projects_hierarchical')
        has_tree_structure = hasattr(project_manager, 'show_tree')
        
        print(f"  Иерархический список: {'✓' if has_hierarchical_list else '✗'}")
        print(f"  Древовидная структура: {'✓' if has_tree_structure else '✗'}")
        
        return hierarchy_support and has_tree_structure
        
    except Exception as e:
        print(f"  Ошибка тестирования иерархии: {e}")
        return False


def test_migration_readiness():
    """Тест готовности к миграции"""
    print("\n=== Тест миграции ===")
    
    try:
        import project_manager
        from core.compatibility import detect_db_format, check_migration_status
        
        data, _ = project_manager.load_db()
        db_format = detect_db_format(data)
        
        print(f"  Текущий формат БД: {db_format}")
        
        if db_format == 'new':
            migration_ready = check_migration_status(data)
            print(f"  Готовность к очистке legacy: {'✓' if migration_ready else '✗'}")
        elif db_format == 'old':
            print("  БД готова к миграции в новый формат")
        
        # Проверяем функцию миграции
        has_migrate_function = hasattr(project_manager, 'migrate_to_new_format')
        print(f"  Функция миграции: {'✓' if has_migrate_function else '✗'}")
        
        return has_migrate_function
        
    except Exception as e:
        print(f"  Ошибка тестирования миграции: {e}")
        return False


def main():
    """Запуск тестов менеджера проектов"""
    print("Тестирование project_manager.py")
    print("=" * 50)
    
    test1 = test_new_commands()
    test2 = test_hierarchy_display()
    test3 = test_migration_readiness()
    
    print("=" * 50)
    
    passed_tests = sum([test1, test2, test3])
    total_tests = 3
    
    print(f"Тестов пройдено: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("Тесты менеджера завершены успешно!")
        return True
    else:
        print("Есть проблемы с некоторыми тестами")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
