"""
Модуль для работы с иерархией проектов
Алгоритмы расчета aggregated_minutes и управления parent/child отношениями
"""


def find_project_by_path(path, projects_list):
    """
    Находит проект по path
    
    Args:
        path (str): Path проекта
        projects_list (list): Список всех проектов
        
    Returns:
        dict|None: Найденный проект или None
    """
    for project in projects_list:
        if project.get('path') == path:
            return project
    return None


def find_project_by_id(project_id, projects_list):
    """
    Находит проект по ID
    
    Args:
        project_id (str): ID проекта
        projects_list (list): Список всех проектов
        
    Returns:
        dict|None: Найденный проект или None
    """
    for project in projects_list:
        if project.get('id') == project_id:
            return project
    return None


def is_direct_child(child_path, parent_path):
    """
    Проверяет, является ли проект прямым ребенком родителя
    
    Args:
        child_path (str): Path потенциального ребенка
        parent_path (str): Path родителя
        
    Returns:
        bool: True если это прямой ребенок
        
    Examples:
        >>> is_direct_child("exlibrus/frontend", "exlibrus")
        True
        >>> is_direct_child("exlibrus/frontend/components", "exlibrus")
        False
        >>> is_direct_child("other/project", "exlibrus")
        False
    """
    if not child_path.startswith(parent_path + "/"):
        return False
    
    # Убираем родительский путь и проверяем что осталось только один уровень
    remaining = child_path[len(parent_path + "/"):]
    return "/" not in remaining


def get_direct_children(parent_path, projects_list):
    """
    Получает всех прямых детей проекта
    
    Args:
        parent_path (str): Path родительского проекта
        projects_list (list): Список всех проектов
        
    Returns:
        list: Список прямых дочерних проектов
    """
    children = []
    for project in projects_list:
        project_path = project.get('path', '')
        if is_direct_child(project_path, parent_path):
            children.append(project)
    return children


def get_all_descendants(parent_path, projects_list):
    """
    Получает всех потомков проекта (на всех уровнях)
    
    Args:
        parent_path (str): Path родительского проекта
        projects_list (list): Список всех проектов
        
    Returns:
        list: Список всех потомков
    """
    descendants = []
    for project in projects_list:
        project_path = project.get('path', '')
        if project_path.startswith(parent_path + "/"):
            descendants.append(project)
    return descendants


def get_all_parent_paths(project_path):
    """
    Возвращает все родительские пути от прямого родителя до корня
    
    Args:
        project_path (str): Path проекта
        
    Returns:
        list: Список родительских путей
        
    Examples:
        >>> get_all_parent_paths("a/b/c/d")
        ['a/b/c', 'a/b', 'a']
        >>> get_all_parent_paths("exlibrus")
        []
    """
    parents = []
    parts = project_path.split("/")
    
    for i in range(len(parts) - 1, 0, -1):
        parent_path = "/".join(parts[:i])
        parents.append(parent_path)
    
    return parents


def get_project_level(project_path):
    """
    Определяет уровень вложенности проекта
    
    Args:
        project_path (str): Path проекта
        
    Returns:
        int: Уровень (0 для корневых проектов)
        
    Examples:
        >>> get_project_level("exlibrus")
        0
        >>> get_project_level("exlibrus/frontend")
        1
        >>> get_project_level("b24/aktiviti/otchety")
        2
    """
    return project_path.count("/")


def calculate_aggregated_minutes(project_path, projects_list):
    """
    Вычисляет aggregated_minutes для проекта
    
    Алгоритм:
    1. Найти проект по path
    2. Получить его total_minutes (собственное время)
    3. Найти всех прямых детей
    4. Рекурсивно просуммировать aggregated_minutes всех детей
    5. Вернуть: total_minutes + сумма_детей
    
    Args:
        project_path (str): Path проекта
        projects_list (list): Список всех проектов
        
    Returns:
        int: Aggregated minutes для проекта
    """
    # Найти текущий проект
    current_project = find_project_by_path(project_path, projects_list)
    if not current_project:
        return 0
    
    own_minutes = current_project.get('total_minutes', 0)
    
    # Найти всех прямых детей и рекурсивно просуммировать их aggregated_minutes
    children_sum = 0
    direct_children = get_direct_children(project_path, projects_list)
    
    for child in direct_children:
        child_path = child.get('path', '')
        children_sum += calculate_aggregated_minutes(child_path, projects_list)
    
    return own_minutes + children_sum


def update_aggregated_minutes(changed_project_path, projects_list):
    """
    Обновляет aggregated_minutes для проекта и всех его родителей
    
    Вызывается после любого изменения total_minutes
    
    Args:
        changed_project_path (str): Path проекта, у которого изменился total_minutes
        projects_list (list): Список всех проектов (изменяется in-place)
        
    Returns:
        list: Список path проектов, которые были обновлены
    """
    # Получить все родительские пути
    parent_paths = get_all_parent_paths(changed_project_path)
    
    # Обновить сначала измененный проект, потом всех родителей
    all_paths_to_update = [changed_project_path] + parent_paths
    updated_paths = []
    
    for path in all_paths_to_update:
        project = find_project_by_path(path, projects_list)
        if project:
            old_aggregated = project.get('aggregated_minutes', 0)
            new_aggregated = calculate_aggregated_minutes(path, projects_list)
            project['aggregated_minutes'] = new_aggregated
            updated_paths.append(path)
    
    return updated_paths


def validate_hierarchy_integrity(projects_list):
    """
    Проверяет целостность иерархии проектов
    
    Args:
        projects_list (list): Список всех проектов
        
    Returns:
        tuple: (is_valid, errors_list)
    """
    errors = []
    
    # Проверка уникальности path и id
    paths = set()
    ids = set()
    
    for project in projects_list:
        path = project.get('path', '')
        project_id = project.get('id', '')
        
        # Проверка уникальности path
        if path in paths:
            errors.append(f"Дублирующийся path: {path}")
        else:
            paths.add(path)
        
        # Проверка уникальности id
        if project_id in ids:
            errors.append(f"Дублирующийся id: {project_id}")
        else:
            ids.add(project_id)
    
    return len(errors) == 0, errors


def get_projects_tree_structure(projects_list):
    """
    Возвращает древовидную структуру проектов для отображения
    
    Args:
        projects_list (list): Список всех проектов
        
    Returns:
        list: Список проектов, отсортированных для древовидного отображения
    """
    # Сортируем проекты по path для правильного порядка отображения
    sorted_projects = sorted(projects_list, key=lambda p: p.get('path', ''))
    
    tree_items = []
    
    for project in sorted_projects:
        path = project.get('path', '')
        level = get_project_level(path)
        
        tree_items.append({
            'project': project,
            'level': level,
            'indent': '  ' * level  # Отступ для визуального отображения
        })
    
    return tree_items


if __name__ == "__main__":
    # Тесты иерархии
    print("=== Тесты работы с иерархией ===")
    
    # Тестовые данные
    test_projects = [
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
    
    print("Тест расчета aggregated_minutes:")
    for project in test_projects:
        path = project['path']
        aggregated = calculate_aggregated_minutes(path, test_projects)
        print(f"  {path}: {project['total_minutes']} собственных + дети = {aggregated} общих")
