"""
Модуль совместимости для поддержки старого и нового форматов БД
TODO: LEGACY_SUPPORT - удалить после миграции всех инстансов
"""
from .transliteration import generate_id_from_title, generate_path_from_title


def detect_db_format(data):
    """
    Определяет формат базы данных
    TODO: LEGACY_SUPPORT - упростить после отказа от старого формата
    
    Args:
        data (dict): Данные из db.json
        
    Returns:
        str: 'old', 'new', 'empty'
    """
    if not data or 'projects' not in data:
        return 'empty'
    
    if not data['projects']:
        return 'empty'
    
    # Проверяем первый проект на наличие новых полей
    first_project = data['projects'][0]
    
    has_id = 'id' in first_project
    has_path = 'path' in first_project  
    has_aggregated = 'aggregated_minutes' in first_project
    
    # Если все новые поля присутствуют - новый формат
    if has_id and has_path and has_aggregated:
        return 'new'
    
    # Если есть хотя бы одно новое поле - частично мигрированный
    if has_id or has_path or has_aggregated:
        return 'partial'
    
    # Если новых полей нет - старый формат
    return 'old'


def ensure_project_fields(project):
    """
    Генерирует недостающие поля для совместимости со старым форматом
    TODO: LEGACY_SUPPORT - удалить после миграции
    
    Args:
        project (dict): Проект из БД
        
    Returns:
        dict: Проект с гарантированными полями id, path, aggregated_minutes
    """
    # Генерируем id если отсутствует
    if 'id' not in project:
        project['id'] = generate_id_from_title(project['title'])
    
    # Генерируем path если отсутствует  
    if 'path' not in project:
        project['path'] = generate_path_from_title(project['title'])
    
    # Устанавливаем aggregated_minutes равным total_minutes если отсутствует
    if 'aggregated_minutes' not in project:
        project['aggregated_minutes'] = project.get('total_minutes', 0)
    
    return project


def get_aggregated_minutes_compat(project):
    """
    Получает aggregated_minutes с поддержкой старого формата
    TODO: LEGACY_SUPPORT - в старом формате aggregated_minutes = total_minutes
    
    Args:
        project (dict): Проект из БД
        
    Returns:
        int: Значение aggregated_minutes
    """
    return project.get('aggregated_minutes', project.get('total_minutes', 0))


def get_project_id_compat(project):
    """
    Получает ID проекта с поддержкой старого формата
    TODO: LEGACY_SUPPORT - генерирует ID из title если отсутствует
    
    Args:
        project (dict): Проект из БД
        
    Returns:
        str: ID проекта
    """
    if 'id' in project:
        return project['id']
    return generate_id_from_title(project['title'])


def get_project_path_compat(project):
    """
    Получает path проекта с поддержкой старого формата
    TODO: LEGACY_SUPPORT - генерирует path из title если отсутствует
    
    Args:
        project (dict): Проект из БД
        
    Returns:
        str: Path проекта
    """
    if 'path' in project:
        return project['path']
    return generate_path_from_title(project['title'])


def check_migration_status(data):
    """
    Проверяет готовность к удалению legacy кода
    TODO: LEGACY_SUPPORT - функция для определения готовности к очистке
    
    Args:
        data (dict): Данные из db.json
        
    Returns:
        bool: True если БД в новом формате и готова к очистке legacy кода
    """
    db_format = detect_db_format(data)
    
    if db_format != 'new':
        return False
    
    # Дополнительные проверки корректности данных
    for project in data['projects']:
        # Проверяем наличие всех обязательных полей
        required_fields = ['id', 'path', 'aggregated_minutes', 'title', 'status', 'total_minutes']
        for field in required_fields:
            if field not in project:
                return False
        
        # Проверяем корректность aggregated_minutes (должно быть >= total_minutes)
        if project['aggregated_minutes'] < project['total_minutes']:
            return False
    
    return True


def legacy_find_project_by_title(projects, title):
    """
    Поиск проекта по title (работает в обоих форматах)
    TODO: LEGACY_SUPPORT - основной способ поиска в старом формате
    
    Args:
        projects (list): Список проектов
        title (str): Название проекта
        
    Returns:
        dict|None: Найденный проект или None
    """
    for project in projects:
        if project['title'].lower() == title.lower():
            return project
    return None


def format_project_display_compat(project, db_format):
    """
    Форматирует отображение проекта в зависимости от формата БД
    TODO: LEGACY_SUPPORT - адаптивный вывод
    
    Args:
        project (dict): Проект
        db_format (str): Формат БД ('old', 'new')
        
    Returns:
        str: Отформатированная строка для вывода
    """
    title = project['title']
    status = project['status']
    total_mins = project.get('total_minutes', 0)
    
    if db_format == 'old':
        # Простой формат для старой БД
        hours = total_mins // 60
        mins = total_mins % 60
        return f"{title} [{status}] ({hours}ч {mins}м)"
    
    else:
        # Расширенный формат для новой БД
        aggregated_mins = project.get('aggregated_minutes', total_mins)
        path = project.get('path', 'unknown')
        
        total_hours = total_mins // 60
        total_mins_rem = total_mins % 60
        agg_hours = aggregated_mins // 60
        agg_mins_rem = aggregated_mins % 60
        
        return f"{title} [{status}] ({total_hours}ч {total_mins_rem}м / {agg_hours}ч {agg_mins_rem}м) [{path}]"


if __name__ == "__main__":
    # Тесты совместимости
    print("=== Тесты детекции формата БД ===")
    
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
    print(f"Старый формат: {detect_db_format(old_data)}")
    
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
    print(f"Новый формат: {detect_db_format(new_data)}")
    
    # Пустая БД
    empty_data = {"projects": []}
    print(f"Пустая БД: {detect_db_format(empty_data)}")
    
    print("\n=== Тест генерации полей ===")
    old_project = {
        "title": "Б24 Отчеты",
        "status": "active",
        "total_minutes": 120
    }
    
    enhanced_project = ensure_project_fields(old_project.copy())
    print(f"Исходный проект: {old_project}")
    print(f"С добавленными полями: {enhanced_project}")
    
    print(f"\nСтатус миграции старой БД: {check_migration_status(old_data)}")
    print(f"Статус миграции новой БД: {check_migration_status(new_data)}")
