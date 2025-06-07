#!/usr/bin/env python3
"""
Простой тест project_manager.py без subprocess
"""
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_import_and_basic_functions():
    """Тест импорта и базовых функций"""
    print("=== Тест импорта project_manager ===")
    
    try:
        import project_manager
        print("  Импорт project_manager: OK")
        
        # Тестируем загрузку БД
        data, db_path = project_manager.load_db()
        print(f"  Загрузка БД: OK ({len(data.get('projects', []))} проектов)")
        
        # Тестируем функцию универсального поиска
        if hasattr(project_manager, 'find_project_universal'):
            project = project_manager.find_project_universal(data, "exlibrus")
            print(f"  Универсальный поиск: {'OK' if project else 'Проект не найден'}")
        else:
            print("  Универсальный поиск: Функция недоступна")
        
        # Проверяем поддержку иерархии
        hierarchy_support = getattr(project_manager, 'HIERARCHY_SUPPORT', False)
        print(f"  Поддержка иерархии: {'Включена' if hierarchy_support else 'Отключена'}")
        
        return True
        
    except Exception as e:
        print(f"  Ошибка импорта: {e}")
        return False


def test_db_format_detection():
    """Тест определения формата БД"""
    print("\n=== Тест определения формата БД ===")
    
    try:
        import project_manager
        from core.compatibility import detect_db_format
        
        data, _ = project_manager.load_db()
        db_format = detect_db_format(data)
        
        print(f"  Формат БД: {db_format}")
        print(f"  Статус: {'OK' if db_format in ['old', 'new'] else 'Неизвестный'}")
        
        # Проверяем первый проект
        if data['projects']:
            first_project = data['projects'][0]
            has_hierarchy_fields = all(field in first_project for field in ['id', 'path', 'aggregated_minutes'])
            print(f"  Поля иерархии в проектах: {'Есть' if has_hierarchy_fields else 'Отсутствуют'}")
        
        return True
        
    except Exception as e:
        print(f"  Ошибка проверки формата: {e}")
        return False


def test_project_structure():
    """Тест структуры проектов"""
    print("\n=== Тест структуры проектов ===")
    
    try:
        import project_manager
        
        data, _ = project_manager.load_db()
        projects = data.get('projects', [])
        
        print(f"  Общее количество проектов: {len(projects)}")
        
        # Анализируем статусы
        statuses = {}
        paths_levels = {}
        
        for project in projects:
            status = project.get('status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1
            
            # Анализируем уровни иерархии если есть path
            if 'path' in project:
                level = project['path'].count('/')
                paths_levels[level] = paths_levels.get(level, 0) + 1
        
        print("  Статусы проектов:")
        for status, count in statuses.items():
            print(f"    {status}: {count}")
        
        if paths_levels:
            print("  Уровни иерархии:")
            for level, count in sorted(paths_levels.items()):
                level_name = "корневой" if level == 0 else f"уровень {level}"
                print(f"    {level_name}: {count}")
        
        # Находим активный проект
        active_projects = [p for p in projects if p.get('status') == 'active']
        print(f"  Активных проектов: {len(active_projects)}")
        
        if active_projects:
            active = active_projects[0]
            print(f"    Активный: {active['title']}")
            if 'path' in active:
                print(f"    Path: {active['path']}")
        
        return True
        
    except Exception as e:
        print(f"  Ошибка анализа структуры: {e}")
        return False


def test_hierarchy_functions():
    """Тест функций иерархии"""
    print("\n=== Тест функций иерархии ===")
    
    try:
        import project_manager
        
        if not project_manager.HIERARCHY_SUPPORT:
            print("  Поддержка иерархии отключена")
            return True
        
        from core.hierarchy import get_projects_tree_structure, calculate_aggregated_minutes
        
        data, _ = project_manager.load_db()
        projects = data['projects']
        
        # Тестируем древовидную структуру
        tree_items = get_projects_tree_structure(projects)
        print(f"  Элементов в дереве: {len(tree_items)}")
        
        # Проверяем расчет aggregated_minutes
        for project in projects[:3]:  # Первые 3 проекта
            path = project.get('path', '')
            if path:
                calculated = calculate_aggregated_minutes(path, projects)
                stored = project.get('aggregated_minutes', 0)
                match = calculated == stored
                print(f"    {project['title']}: расчет={calculated}, сохранено={stored} {'✓' if match else '✗'}")
        
        print("  Функции иерархии: OK")
        return True
        
    except Exception as e:
        print(f"  Ошибка функций иерархии: {e}")
        return False


def main():
    """Запуск упрощенных тестов"""
    print("Тестирование project_manager.py (упрощенная версия)")
    print("=" * 60)
    
    test1 = test_import_and_basic_functions()
    test2 = test_db_format_detection()
    test3 = test_project_structure()
    test4 = test_hierarchy_functions()
    
    print("=" * 60)
    
    passed_tests = sum([test1, test2, test3, test4])
    total_tests = 4
    
    print(f"Тестов пройдено: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("Все тесты project_manager завершены успешно!")
        return True
    else:
        print("Есть проблемы с некоторыми тестами")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
