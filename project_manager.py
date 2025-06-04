#!/usr/bin/env python3
"""
Утилита для управления проектами и статусами
"""
import json
import os
import sys

def load_db():
    """Загружает базу данных"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'db.json')
    
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f), db_path

def save_db(data, db_path):
    """Сохраняет базу данных"""
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def list_projects():
    """Показывает все проекты и их статусы"""
    data, _ = load_db()
    
    print("=== Список проектов ===")
    for i, project in enumerate(data['projects'], 1):
        status = project['status']
        title = project['title']
        minutes = project.get('total_minutes', 0)
        hours = minutes // 60
        mins = minutes % 60
        
        marker = ">" if status == "active" else " "
        print(f"{marker} {i}. {title}")
        print(f"    Статус: {status}")
        print(f"    Время: {hours}ч {mins}м ({minutes} мин)")
        print()

def set_active_project(project_title):
    """Делает проект активным"""
    data, db_path = load_db()
    
    # Сначала все проекты делаем неактивными
    for project in data['projects']:
        if project['status'] == 'active':
            project['status'] = 'paused'
    
    # Находим нужный проект и делаем активным
    for project in data['projects']:
        if project['title'].lower() == project_title.lower():
            project['status'] = 'active'
            save_db(data, db_path)
            print(f"OK Проект '{project['title']}' теперь активный")
            return True
    
    print(f"ОШИБКА Проект '{project_title}' не найден")
    return False

def set_project_status(project_title, new_status):
    """Устанавливает статус проекта"""
    valid_statuses = ['active', 'paused', 'completed', 'archived']
    
    if new_status not in valid_statuses:
        print(f"ОШИБКА Неверный статус. Доступны: {', '.join(valid_statuses)}")
        return False
    
    data, db_path = load_db()
    
    # Если устанавливаем active, сначала убираем active у других
    if new_status == 'active':
        for project in data['projects']:
            if project['status'] == 'active':
                project['status'] = 'paused'
    
    # Находим проект и устанавливаем статус
    for project in data['projects']:
        if project['title'].lower() == project_title.lower():
            old_status = project['status']
            project['status'] = new_status
            save_db(data, db_path)
            print(f"OK Статус проекта '{project['title']}': {old_status} → {new_status}")
            return True
    
    print(f"ОШИБКА Проект '{project_title}' не найден")
    return False

def main():
    """Главная функция CLI"""
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python project_manager.py list                    - показать все проекты")
        print("  python project_manager.py active <название>       - сделать проект активным")
        print("  python project_manager.py status <название> <статус> - установить статус")
        print()
        print("Доступные статусы: active, paused, completed, archived")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_projects()
    
    elif command == 'active' and len(sys.argv) >= 3:
        project_name = ' '.join(sys.argv[2:])
        set_active_project(project_name)
    
    elif command == 'status' and len(sys.argv) >= 4:
        project_name = ' '.join(sys.argv[2:-1])
        status = sys.argv[-1].lower()
        set_project_status(project_name, status)
    
    else:
        print("ОШИБКА Неверная команда")

if __name__ == "__main__":
    main()
