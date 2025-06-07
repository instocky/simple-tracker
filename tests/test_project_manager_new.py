#!/usr/bin/env python3
"""
Тесты для расширенного project_manager.py
Проверка новых команд и иерархической функциональности
"""
import sys
import os
import json
import tempfile
import shutil

# Добавляем путь к проекту для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_db_info_command():
    """Тест команды info"""
    print("=== Тест команды info ===")
    
    # Запускаем команду info
    import subprocess
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        result = subprocess.run([
            'python', 'project_manager.py', 'info'
        ], cwd=script_dir, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("  Команда info: OK")
            output_lines = result.stdout.split('\n')
            
            # Проверяем наличие ключевых элементов
            has_projects_count = any('Проектов:' in line for line in output_lines)
            has_format = any('Формат:' in line for line in output_lines)
            has_statuses = any('Статусы проектов:' in line for line in output_lines)
            
            print(f"    Количество проектов: {'✓' if has_projects_count else '✗'}")
            print(f"    Формат БД: {'✓' if has_format else '✗'}")
            print(f"    Статистика: {'✓' if has_statuses else '✗'}")
            
            return has_projects_count and has_format and has_statuses
        else:
            print(f"  Ошибка команды info: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  Исключение при тесте info: {e}")
        return False


def test_tree_command():
    """Тест команды tree"""
    print("\n=== Тест команды tree ===")
    
    import subprocess
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        result = subprocess.run([
            'python', 'project_manager.py', 'tree'
        ], cwd=script_dir, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("  Команда tree: OK")
            output_lines = result.stdout.split('\n')
            
            # Проверяем структуру вывода
            has_header = any('Древовидная структура' in line for line in output_lines)
            has_projects = len([line for line in output_lines if '[' in line and ']' in line]) > 0
            has_indentation = any(line.startswith('  ') or line.startswith('- ') for line in output_lines)
            
            print(f"    Заголовок: {'✓' if has_header else '✗'}")
            print(f"    Проекты найдены: {'✓' if has_projects else '✗'}")
            print(f"    Отступы иерархии: {'✓' if has_indentation else '✗'}")
            
            return has_header and has_projects
        else:
            print(f"  Ошибка команды tree: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  Исключение при тесте tree: {e}")
        return False


def test_universal_search():
    """Тест универсального поиска проектов"""
    print("\n=== Тест универсального поиска ===")
    
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(script_dir, 'db.json')
    
    try:
        # Загружаем БД
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Импортируем функцию поиска
        import project_manager
        
        print("  Тестируем поиск проектов...")
        
        # Тест поиска по title
        project1 = project_manager.find_project_universal(data, "exlibrus")
        print(f"    Поиск по title 'exlibrus': {'✓' if project1 else '✗'}")
        
        # Тест поиска по path (если есть иерархия)
        project2 = project_manager.find_project_universal(data, "exlibrus/frontend")  
        print(f"    Поиск по path 'exlibrus/frontend': {'✓' if project2 else 'N/A'}")
        
        # Тест поиска по ID
        project3 = project_manager.find_project_universal(data, "b24-paused")
        print(f"    Поиск по ID 'b24-paused': {'✓' if project3 else '✗'}")
        
        return bool(project1 and project3)
        
    except Exception as e:
        print(f"  Исключение при тесте поиска: {e}")
        return False


def test_hierarchy_display():
    """Тест отображения иерархии"""
    print("\n=== Тест отображения иерархии ===")
    
    import subprocess
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Тестируем команду list с новым форматом
        result = subprocess.run([
            'python', 'project_manager.py', 'list'
        ], cwd=script_dir, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("  Команда list: OK")
            output = result.stdout
            
            # Проверяем элементы иерархического отображения
            has_format_indicator = 'формат' in output.lower()
            has_path_info = 'Path:' in output
            has_time_format = '/' in output and 'мин' in output  # формат "собственное/общее"
            has_status_markers = '[active]' in output or '[paused]' in output
            
            print(f"    Индикатор формата: {'✓' if has_format_indicator else '✗'}")
            print(f"    Информация о path: {'✓' if has_path_info else '✗'}")
            print(f"    Формат времени: {'✓' if has_time_format else '✗'}")
            print(f"    Маркеры статуса: {'✓' if has_status_markers else '✗'}")
            
            return has_path_info and has_status_markers
        else:
            print(f"  Ошибка команды list: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  Исключение при тесте отображения: {e}")
        return False


def test_help_command():
    """Тест команды help"""
    print("\n=== Тест команды help ===")
    
    import subprocess
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        result = subprocess.run([
            'python', 'project_manager.py', 'help'
        ], cwd=script_dir, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("  Команда help: OK")
            output = result.stdout
            
            # Проверяем наличие новых команд в справке
            has_tree_cmd = 'tree' in output
            has_info_cmd = 'info' in output  
            has_create_cmd = 'create' in output
            has_migrate_cmd = 'migrate' in output
            has_search_info = 'path' in output.lower()
            
            print(f"    Команда tree: {'✓' if has_tree_cmd else '✗'}")
            print(f"    Команда info: {'✓' if has_info_cmd else '✗'}")
            print(f"    Команда create: {'✓' if has_create_cmd else '✗'}")
            print(f"    Команда migrate: {'✓' if has_migrate_cmd else '✗'}")
            print(f"    Информация о поиске: {'✓' if has_search_info else '✗'}")
            
            return has_tree_cmd and has_info_cmd and has_create_cmd
        else:
            print(f"  Ошибка команды help: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  Исключение при тесте help: {e}")
        return False


def main():
    """Запуск всех тестов project_manager"""
    print("Тестирование расширенного project_manager.py")
    print("=" * 60)
    
    # Запускаем тесты
    test1 = test_help_command()
    test2 = test_db_info_command()
    test3 = test_tree_command()
    test4 = test_universal_search()
    test5 = test_hierarchy_display()
    
    print("=" * 60)
    
    passed_tests = sum([test1, test2, test3, test4, test5])
    total_tests = 5
    
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
