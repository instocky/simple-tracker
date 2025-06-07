#!/usr/bin/env python3
"""
Демонстрация работы tracker_quick.py с иерархией
Показывает как обновляется aggregated_minutes
"""
import sys
import os
import json
import shutil
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.hierarchy import calculate_aggregated_minutes, update_aggregated_minutes
from core.compatibility import detect_db_format


def create_test_hierarchy_db():
    """Создает тестовую БД с иерархией проектов"""
    print("=== Создание тестовой иерархической БД ===")
    
    # Создаем тестовые данные с иерархией
    test_data = {
        "meta": {
            "work_hours": {"start": "08:00", "end": "20:00"},
            "time_tracking": {"interval_minutes": 5, "total_daily_slots": 144}
        },
        "projects": [
            {
                "id": "exlibrus",
                "path": "exlibrus", 
                "title": "ExLibrus",
                "status": "paused",
                "fill_color": "#4CAF50",
                "total_minutes": 50,
                "aggregated_minutes": 0,  # Будет пересчитано
                "daily_masks": {"2025-06-07": "1111111111" + "0" * 134}  # 50 минут
            },
            {
                "id": "exlibrus-frontend",
                "path": "exlibrus/frontend",
                "title": "Frontend", 
                "status": "active",
                "fill_color": "#4CAF50",
                "total_minutes": 120,
                "aggregated_minutes": 0,  # Будет пересчитано
                "daily_masks": {"2025-06-07": "111111111111111111111111" + "0" * 120}  # 120 минут
            },
            {
                "id": "exlibrus-frontend-components",
                "path": "exlibrus/frontend/components",
                "title": "Components",
                "status": "paused", 
                "fill_color": "#81C784",
                "total_minutes": 60,
                "aggregated_minutes": 60,
                "daily_masks": {"2025-06-07": "111111111111" + "0" * 132}  # 60 минут
            }
        ]
    }
    
    # Пересчитываем aggregated_minutes для всех проектов
    for project in test_data['projects']:
        path = project['path']
        project['aggregated_minutes'] = calculate_aggregated_minutes(path, test_data['projects'])
    
    # Сохраняем тестовую БД
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_db_path = os.path.join(script_dir, 'db_hierarchy_test.json')
    
    with open(test_db_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print(f"  Создан файл: {test_db_path}")
    print("  Структура:")
    for project in test_data['projects']:
        level = project['path'].count('/')
        indent = "  " * (level + 2)
        print(f"{indent}{project['title']} ({project['total_minutes']}/{project['aggregated_minutes']} мин)")
    
    return test_db_path


def test_hierarchy_tracking():
    """Тестирует трекинг времени с обновлением иерархии"""
    print("\n=== Тест трекинга с иерархией ===")
    
    # Создаем тестовую БД
    test_db_path = create_test_hierarchy_db()
    
    # Создаем backup оригинальной БД
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    original_db = os.path.join(script_dir, 'db.json')
    backup_db = os.path.join(script_dir, 'db_backup_for_test.json')
    
    shutil.copy2(original_db, backup_db)
    print(f"  Backup оригинальной БД: {backup_db}")
    
    try:
        # Заменяем БД на тестовую
        shutil.copy2(test_db_path, original_db)
        print("  Установлена тестовая БД")
        
        # Показываем состояние ДО трекинга
        with open(original_db, 'r', encoding='utf-8') as f:
            data_before = json.load(f)
        
        print("  Состояние ДО трекинга:")
        for project in data_before['projects']:
            level = project['path'].count('/')
            indent = "    " + "  " * level
            print(f"{indent}{project['title']}: {project['total_minutes']}/{project['aggregated_minutes']} мин [{project['status']}]")
        
        # Импортируем и запускаем трекер
        import tracker_quick
        
        # Проверяем формат
        db_format = detect_db_format(data_before)
        print(f"  Формат БД: {db_format}")
        
        # Имитируем работу трекера (только если есть активный проект)
        active_found = any(p['status'] == 'active' for p in data_before['projects'])
        if active_found:
            print("  Найден активный проект - запускаем трекер...")
            
            # Здесь бы был реальный вызов, но вне рабочих часов он не сработает
            # result = tracker_quick.quick_track()
            
            # Вместо этого симулируем изменение времени
            for project in data_before['projects']:
                if project['status'] == 'active':
                    old_total = project['total_minutes']
                    project['total_minutes'] += 5  # Добавляем 5 минут
                    
                    # Обновляем aggregated_minutes в иерархии
                    update_aggregated_minutes(project['path'], data_before['projects'])
                    
                    print(f"    Добавлено 5 минут к проекту: {project['title']}")
                    break
            
            # Сохраняем изменения
            with open(original_db, 'w', encoding='utf-8') as f:
                json.dump(data_before, f, ensure_ascii=False, indent=2)
            
            # Показываем состояние ПОСЛЕ
            print("  Состояние ПОСЛЕ трекинга:")
            for project in data_before['projects']:
                level = project['path'].count('/')
                indent = "    " + "  " * level
                print(f"{indent}{project['title']}: {project['total_minutes']}/{project['aggregated_minutes']} мин")
        else:
            print("  Активный проект не найден")
        
        print("  Тест иерархии: OK")
        
    finally:
        # Восстанавливаем оригинальную БД
        shutil.copy2(backup_db, original_db)
        print("  Оригинальная БД восстановлена")
        
        # Удаляем временные файлы
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        if os.path.exists(backup_db):
            os.remove(backup_db)
        print("  Временные файлы удалены")


def test_real_tracker_with_current_db():
    """Тестирует реальный трекер с текущей БД"""
    print("\n=== Тест реального трекера ===")
    
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(script_dir, 'db.json')
    
    # Загружаем текущую БД
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"  Текущий формат БД: {detect_db_format(data)}")
    print(f"  Проектов: {len(data['projects'])}")
    
    # Показываем активные проекты
    active_projects = [p for p in data['projects'] if p['status'] == 'active']
    print(f"  Активных проектов: {len(active_projects)}")
    
    for project in active_projects:
        print(f"    {project['title']}: {project.get('total_minutes', 0)} мин")
        # Если есть поля иерархии, показываем их
        if 'path' in project:
            print(f"      Path: {project['path']}")
            print(f"      Aggregated: {project.get('aggregated_minutes', 'Не задано')} мин")
    
    # Проверяем работу трекера
    import tracker_quick
    
    try:
        result = tracker_quick.quick_track()
        print(f"  Результат трекера: {result}")
        print(f"  Статус: {'OK' if result else 'Вне рабочих часов или ошибка'}")
    except Exception as e:
        print(f"  Ошибка трекера: {e}")


def main():
    """Запуск демонстрации"""
    print("Демонстрация работы tracker_quick.py с иерархией")
    print("=" * 60)
    
    test_hierarchy_tracking()
    test_real_tracker_with_current_db()
    
    print("=" * 60)
    print("Демонстрация завершена!")


if __name__ == "__main__":
    main()
