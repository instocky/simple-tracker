#!/usr/bin/env python3
"""
Утилита для управления проектами и статусами
Версия с поддержкой иерархических проектов
"""
import json
import os
import sys
import shutil
from datetime import datetime

# Импорт core модулей для работы с иерархией
try:
    from core.compatibility import (
        detect_db_format, ensure_project_fields, check_migration_status,
        legacy_find_project_by_title, format_project_display_compat
    )
    from core.hierarchy import (
        find_project_by_path, find_project_by_id, get_projects_tree_structure,
        update_aggregated_minutes, validate_hierarchy_integrity
    )
    from core.transliteration import (
        generate_id_from_title, generate_path_from_title, validate_path
    )
    HIERARCHY_SUPPORT = True
except ImportError:
    # Fallback если core модули недоступны
    HIERARCHY_SUPPORT = False


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


def show_db_info():
    """Показывает информацию о формате БД"""
    data, _ = load_db()
    
    print("=== Информация о базе данных ===")
    print(f"Проектов: {len(data.get('projects', []))}")
    
    if HIERARCHY_SUPPORT:
        db_format = detect_db_format(data)
        print(f"Формат: {db_format}")
        print(f"Поддержка иерархии: Включена")
        
        # Статистика по статусам
        statuses = {}
        for project in data['projects']:
            status = project.get('status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1
        
        print("Статусы проектов:")
        for status, count in statuses.items():
            print(f"  {status}: {count}")
        
        # Проверка готовности к миграции
        if db_format == 'old':
            print("Статус: Готов к миграции в новый формат")
        elif db_format == 'new':
            migration_ready = check_migration_status(data)
            print(f"Статус: Новый формат ({'готов к очистке legacy кода' if migration_ready else 'требует проверки'})")
    else:
        print("Поддержка иерархии: Отключена")
    
    print()


def list_projects():
    """Показывает все проекты и их статусы"""
    data, _ = load_db()
    
    if HIERARCHY_SUPPORT:
        db_format = detect_db_format(data)
        print(f"=== Список проектов ({db_format} формат) ===")
        
        if db_format == 'new':
            # Иерархический вывод
            list_projects_hierarchical(data)
        else:
            # Старый формат с генерацией полей
            list_projects_legacy_compat(data)
    else:
        # Fallback к старому формату
        list_projects_legacy(data)


def list_projects_hierarchical(data):
    """Иерархический вывод проектов (новый формат)"""
    tree_items = get_projects_tree_structure(data['projects'])
    
    for item in tree_items:
        project = item['project']
        indent = item['indent']
        
        title = project['title']
        status = project['status']
        total_mins = project.get('total_minutes', 0)
        aggregated_mins = project.get('aggregated_minutes', total_mins)
        path = project.get('path', 'unknown')
        
        # Форматирование времени
        total_h, total_m = divmod(total_mins, 60)
        agg_h, agg_m = divmod(aggregated_mins, 60)
        
        # Маркер активности
        marker = ">" if status == "active" else " "
        
        print(f"{marker}{indent}{title} [{status}]")
        print(f" {indent}  Время: {total_h}ч {total_m}м / {agg_h}ч {agg_m}м ({total_mins}/{aggregated_mins} мин)")
        print(f" {indent}  Path: {path}")
        print()


def list_projects_legacy_compat(data):
    """Вывод с совместимостью (старый формат с auto-генерацией полей)"""
    print("Примечание: Поля иерархии генерируются автоматически")
    print()
    
    for i, project in enumerate(data['projects'], 1):
        # TODO: LEGACY_SUPPORT - генерируем поля на лету
        enhanced_project = ensure_project_fields(project.copy())
        
        title = enhanced_project['title']
        status = enhanced_project['status']
        total_mins = enhanced_project.get('total_minutes', 0)
        project_id = enhanced_project.get('id', 'unknown')
        path = enhanced_project.get('path', 'unknown')
        
        hours, mins = divmod(total_mins, 60)
        marker = ">" if status == "active" else " "
        
        print(f"{marker} {i}. {title} [{status}]")
        print(f"    Время: {hours}ч {mins}м ({total_mins} мин)")
        print(f"    ID: {project_id}")
        print(f"    Path: {path}")
        print()


def list_projects_legacy(data):
    """Старый формат вывода (fallback)"""
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


def show_tree():
    """Показывает древовидную структуру проектов"""
    data, _ = load_db()
    
    if not HIERARCHY_SUPPORT:
        print("ОШИБКА: Поддержка иерархии отключена")
        return False
    
    db_format = detect_db_format(data)
    if db_format == 'old':
        print("=== Древовидная структура (с auto-генерацией полей) ===")
        # Генерируем поля для совместимости
        for project in data['projects']:
            ensure_project_fields(project)
    else:
        print("=== Древовидная структура проектов ===")
    
    tree_items = get_projects_tree_structure(data['projects'])
    
    if not tree_items:
        print("Проекты не найдены")
        return True
    
    for item in tree_items:
        project = item['project']
        level = item['level']
        
        # Визуальные символы для дерева
        if level == 0:
            prefix = ""
        else:
            prefix = "  " * (level - 1) + "- "
        
        title = project['title']
        status = project['status']
        total_mins = project.get('total_minutes', 0)
        aggregated_mins = project.get('aggregated_minutes', total_mins)
        
        # Форматирование
        total_h, total_m = divmod(total_mins, 60)
        agg_h, agg_m = divmod(aggregated_mins, 60)
        
        status_color = {
            'active': '[АКТИВЕН]',
            'paused': '[пауза]', 
            'completed': '[завершен]',
            'archived': '[архив]'
        }.get(status, f'[{status}]')
        
        print(f"{prefix}{title} {status_color}")
        print(f"{' ' * len(prefix)}  {total_h}ч{total_m}м собств. / {agg_h}ч{agg_m}м общее")
    
    print()
    return True


def find_project_universal(data, identifier):
    """
    Универсальный поиск проекта по title, id или path
    """
    if not HIERARCHY_SUPPORT:
        # TODO: LEGACY_SUPPORT - поиск только по title
        return legacy_find_project_by_title(data['projects'], identifier)
    
    projects = data['projects']
    
    # Пробуем найти по ID
    project = find_project_by_id(identifier, projects)
    if project:
        return project
    
    # Пробуем найти по path
    project = find_project_by_path(identifier, projects)
    if project:
        return project
    
    # Пробуем найти по title
    project = legacy_find_project_by_title(projects, identifier)
    if project:
        return project
    
    return None


def set_active_project(project_identifier):
    """Делает проект активным (поиск по title, id или path)"""
    data, db_path = load_db()
    
    # Сначала все проекты делаем неактивными
    for project in data['projects']:
        if project['status'] == 'active':
            project['status'] = 'paused'
    
    # Находим проект универсальным поиском
    target_project = find_project_universal(data, project_identifier)
    
    if target_project:
        target_project['status'] = 'active'
        
        # Обеспечиваем наличие полей иерархии
        if HIERARCHY_SUPPORT:
            ensure_project_fields(target_project)
        
        save_db(data, db_path)
        print(f"OK Проект '{target_project['title']}' теперь активный")
        
        # Показываем дополнительную информацию
        if HIERARCHY_SUPPORT and 'path' in target_project:
            print(f"   Path: {target_project['path']}")
            print(f"   ID: {target_project.get('id', 'unknown')}")
        
        return True
    
    print(f"ОШИБКА Проект '{project_identifier}' не найден")
    print("Попробуйте поиск по title, id или path")
    return False


def set_project_status(project_identifier, new_status):
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
    
    # Находим проект универсальным поиском
    target_project = find_project_universal(data, project_identifier)
    
    if target_project:
        old_status = target_project['status']
        target_project['status'] = new_status
        
        # Обеспечиваем наличие полей иерархии
        if HIERARCHY_SUPPORT:
            ensure_project_fields(target_project)
        
        save_db(data, db_path)
        print(f"OK Статус проекта '{target_project['title']}': {old_status} -> {new_status}")
        return True
    
    print(f"ОШИБКА Проект '{project_identifier}' не найден")
    return False


def create_project(title, parent_path=None):
    """Создает новый проект"""
    if not HIERARCHY_SUPPORT:
        print("ОШИБКА: Создание проектов требует поддержки иерархии")
        return False
    
    data, db_path = load_db()
    
    try:
        # Генерируем ID и path
        if parent_path:
            # Проверяем что родитель существует
            parent_project = find_project_by_path(parent_path, data['projects'])
            if not parent_project:
                print(f"ОШИБКА: Родительский проект '{parent_path}' не найден")
                return False
            
            project_path = generate_path_from_title(title, parent_path)
        else:
            project_path = generate_path_from_title(title)
        
        # Валидируем path
        validate_path(project_path)
        
        # Проверяем уникальность
        if find_project_by_path(project_path, data['projects']):
            print(f"ОШИБКА: Проект с path '{project_path}' уже существует")
            return False
        
        # Создаем новый проект
        new_project = {
            'id': generate_id_from_title(title),
            'path': project_path,
            'title': title,
            'status': 'paused',
            'fill_color': '#4CAF50',  # Цвет по умолчанию
            'total_minutes': 0,
            'aggregated_minutes': 0,
            'daily_masks': {}
        }
        
        data['projects'].append(new_project)
        
        # Обновляем aggregated_minutes родителей если есть
        if parent_path:
            update_aggregated_minutes(project_path, data['projects'])
        
        save_db(data, db_path)
        
        print(f"OK Проект '{title}' создан")
        print(f"   ID: {new_project['id']}")
        print(f"   Path: {new_project['path']}")
        if parent_path:
            print(f"   Родитель: {parent_path}")
        
        return True
        
    except Exception as e:
        print(f"ОШИБКА при создании проекта: {e}")
        return False


def migrate_to_new_format():
    """Миграция БД в новый формат с иерархией"""
    if not HIERARCHY_SUPPORT:
        print("ОШИБКА: Миграция требует поддержки core модулей")
        return False
    
    data, db_path = load_db()
    
    db_format = detect_db_format(data)
    if db_format == 'new':
        print("БД уже в новом формате")
        return True
    elif db_format == 'empty':
        print("БД пустая, миграция не требуется")
        return True
    
    print("=== Миграция БД в новый формат ===")
    
    # Создаем backup
    backup_path = db_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"Backup создан: {backup_path}")
    
    try:
        print("Обновление проектов...")
        
        # Обрабатываем каждый проект
        for i, project in enumerate(data['projects'], 1):
            print(f"  {i}. {project['title']}")
            
            # Генерируем недостающие поля
            ensure_project_fields(project)
            
            print(f"     ID: {project['id']}")
            print(f"     Path: {project['path']}")
        
        # Пересчитываем aggregated_minutes для всех проектов
        print("Пересчет aggregated_minutes...")
        for project in data['projects']:
            path = project['path']
            from core.hierarchy import calculate_aggregated_minutes
            project['aggregated_minutes'] = calculate_aggregated_minutes(path, data['projects'])
        
        # Проверяем целостность
        is_valid, errors = validate_hierarchy_integrity(data['projects'])
        if not is_valid:
            print("ПРЕДУПРЕЖДЕНИЯ при валидации:")
            for error in errors:
                print(f"  - {error}")
        
        # Добавляем meta информацию если отсутствует
        if 'meta' not in data:
            data['meta'] = {
                "work_hours": {"start": "08:00", "end": "20:00"},
                "time_tracking": {"interval_minutes": 5, "total_daily_slots": 144}
            }
        
        # Сохраняем новый формат
        save_db(data, db_path)
        
        # Проверяем результат
        new_format = detect_db_format(data)
        if new_format == 'new':
            print("Миграция завершена успешно!")
            print(f"Проектов обновлено: {len(data['projects'])}")
            print(f"Backup сохранен: {backup_path}")
            return True
        else:
            print(f"Ошибка миграции: формат остался '{new_format}'")
            return False
            
    except Exception as e:
        print(f"ОШИБКА при миграции: {e}")
        
        # Восстанавливаем из backup
        try:
            shutil.copy2(backup_path, db_path)
            print(f"БД восстановлена из backup: {backup_path}")
        except:
            print("КРИТИЧЕСКАЯ ОШИБКА: Не удалось восстановить БД!")
        
        return False


def show_help():
    """Показывает справку по командам"""
    print("=== Управление проектами Simple Time Tracker ===")
    print()
    print("Основные команды:")
    print("  list                           - показать все проекты")
    print("  active <идентификатор>         - сделать проект активным")
    print("  status <идентификатор> <статус> - установить статус")
    print()
    
    if HIERARCHY_SUPPORT:
        print("Команды иерархии:")
        print("  tree                          - древовидная структура")
        print("  info                          - информация о БД")
        print("  create <название>             - создать корневой проект")
        print("  create <название> --parent <path> - создать дочерний проект")
        print("  migrate                       - миграция в новый формат")
        print()
        print("Поиск проектов:")
        print("  По названию: 'ExLibrus'")
        print("  По ID:       'exlibrus'")
        print("  По path:     'exlibrus/frontend'")
        print()
    
    print("Доступные статусы:")
    print("  active    - активный (идет трекинг)")
    print("  paused    - приостановлен")
    print("  completed - завершен")
    print("  archived  - архивирован")
    print()


def main():
    """Главная функция CLI"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    # Команды без параметров
    if command == 'list':
        list_projects()
    
    elif command == 'tree':
        if not show_tree():
            sys.exit(1)
    
    elif command == 'info':
        show_db_info()
    
    elif command == 'migrate':
        if not migrate_to_new_format():
            sys.exit(1)
    
    elif command == 'help' or command == '--help':
        show_help()
    
    # Команды с параметрами
    elif command == 'active' and len(sys.argv) >= 3:
        project_identifier = ' '.join(sys.argv[2:])
        if not set_active_project(project_identifier):
            sys.exit(1)
    
    elif command == 'status' and len(sys.argv) >= 4:
        project_identifier = ' '.join(sys.argv[2:-1])
        status = sys.argv[-1].lower()
        if not set_project_status(project_identifier, status):
            sys.exit(1)
    
    elif command == 'create':
        if len(sys.argv) < 3:
            print("ОШИБКА: Укажите название проекта")
            sys.exit(1)
        
        # Проверяем наличие --parent
        parent_path = None
        if '--parent' in sys.argv:
            parent_idx = sys.argv.index('--parent')
            if parent_idx + 1 < len(sys.argv):
                parent_path = sys.argv[parent_idx + 1]
                # Убираем --parent и путь из названия
                title_parts = sys.argv[2:parent_idx]
            else:
                print("ОШИБКА: После --parent должен быть указан path родителя")
                sys.exit(1)
        else:
            title_parts = sys.argv[2:]
        
        title = ' '.join(title_parts)
        if not create_project(title, parent_path):
            sys.exit(1)
    
    else:
        print("ОШИБКА: Неверная команда")
        print("Используйте 'help' для справки")
        sys.exit(1)


if __name__ == "__main__":
    main()
