#!/usr/bin/env python3
"""
Ручной тест трекера с возможностью принудительного запуска
"""
import sys
import os
import json
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def manual_track_test():
    """Ручной тест трекера"""
    print("=== Ручной тест трекера ===")
    
    # Загружаем данные
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(script_dir, 'db.json')
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"  Проектов в БД: {len(data['projects'])}")
        
        # Находим активный проект
        active_project = None
        for project in data['projects']:
            if project.get('status') == 'active':
                active_project = project
                break
        
        if active_project:
            print(f"  Активный проект: {active_project['title']}")
            print(f"  Текущее время: {active_project.get('total_minutes', 0)} мин")
            print(f"  Aggregated время: {active_project.get('aggregated_minutes', 'Не задано')} мин")
            
            # Проверяем наличие полей иерархии
            has_hierarchy = all(field in active_project for field in ['id', 'path', 'aggregated_minutes'])
            print(f"  Поля иерархии: {'Есть' if has_hierarchy else 'Генерируются автоматически'}")
            
            if has_hierarchy:
                print(f"    ID: {active_project['id']}")
                print(f"    Path: {active_project['path']}")
        else:
            print("  Активный проект не найден")
        
        # Проверяем формат БД
        from core.compatibility import detect_db_format
        db_format = detect_db_format(data)
        print(f"  Формат БД: {db_format}")
        
        # Тестируем функции иерархии
        if active_project and 'path' in active_project:
            from core.hierarchy import get_all_parent_paths, get_project_level
            
            path = active_project['path']
            level = get_project_level(path)
            parents = get_all_parent_paths(path)
            
            print(f"  Уровень проекта: {level}")
            print(f"  Родители: {parents if parents else 'Нет (корневой проект)'}")
        
        return True
        
    except Exception as e:
        print(f"  ОШИБКА: {e}")
        return False


def check_tracker_performance():
    """Проверка производительности трекера"""
    print("\n=== Тест производительности ===")
    
    import time
    import tracker_quick
    
    # Измеряем время выполнения
    start_time = time.time()
    
    try:
        result = tracker_quick.quick_track()
        end_time = time.time()
        
        execution_time = (end_time - start_time) * 1000  # в миллисекундах
        
        print(f"  Результат: {result}")
        print(f"  Время выполнения: {execution_time:.2f} мс")
        print(f"  Производительность: {'OK' if execution_time < 500 else 'МЕДЛЕННО'}")
        
        return execution_time < 500
        
    except Exception as e:
        print(f"  ОШИБКА производительности: {e}")
        return False


def main():
    """Запуск ручных тестов"""
    print("Ручное тестирование модифицированного tracker_quick.py")
    print("=" * 60)
    
    test1 = manual_track_test()
    test2 = check_tracker_performance()
    
    print("=" * 60)
    
    if test1 and test2:
        print("Все тесты прошли успешно!")
        print("Tracker готов к использованию")
    else:
        print("Есть проблемы с трекером")
    
    return test1 and test2


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
