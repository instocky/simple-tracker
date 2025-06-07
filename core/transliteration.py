"""
Модуль транслитерации для генерации ID и path из названий проектов
"""
import re


# Таблица транслитерации русских букв
TRANSLITERATION_TABLE = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
}


def transliterate(text):
    """
    Транслитерирует текст в латиницу для использования в path
    
    Правила:
    - Русские буквы → латинские аналоги
    - Пробелы → дефисы
    - Специальные символы удаляются
    - Результат приводится к нижнему регистру
    
    Args:
        text (str): Исходный текст
        
    Returns:
        str: Транслитерированный текст
        
    Examples:
        >>> transliterate("Отчеты")
        'otchety'
        >>> transliterate("Б24 Активити")
        'b24-aktiviti'
        >>> transliterate("React Components")
        'react-components'
    """
    if not text:
        return ""
    
    # Транслитерируем русские буквы
    result = ""
    for char in text:
        if char in TRANSLITERATION_TABLE:
            result += TRANSLITERATION_TABLE[char]
        else:
            result += char
    
    # Заменяем пробелы на дефисы
    result = re.sub(r'\s+', '-', result)
    
    # Заменяем точки на дефисы
    result = result.replace('.', '-')
    
    # Оставляем только латиницу, цифры, дефисы
    result = re.sub(r'[^a-zA-Z0-9\-]', '', result)
    
    # Убираем множественные дефисы
    result = re.sub(r'-+', '-', result)
    
    # Убираем дефисы в начале и конце
    result = result.strip('-')
    
    # Приводим к нижнему регистру
    return result.lower()


def generate_id_from_title(title):
    """
    Генерирует уникальный ID проекта из title
    
    Args:
        title (str): Название проекта
        
    Returns:
        str: ID проекта
        
    Examples:
        >>> generate_id_from_title("ExLibrus Frontend")
        'exlibrus-frontend'
        >>> generate_id_from_title("Б24 Отчеты")
        'b24-otchety'
    """
    return transliterate(title)


def generate_path_from_title(title, parent_path=None):
    """
    Генерирует path проекта из title и родительского path
    
    Args:
        title (str): Название проекта
        parent_path (str, optional): Path родительского проекта
        
    Returns:
        str: Path проекта
        
    Examples:
        >>> generate_path_from_title("Frontend")
        'frontend'
        >>> generate_path_from_title("Components", "exlibrus/frontend")
        'exlibrus/frontend/components'
    """
    transliterated = transliterate(title)
    
    if parent_path:
        return f"{parent_path}/{transliterated}"
    else:
        return transliterated


def generate_id_from_path(path):
    """
    Генерирует ID проекта из path (заменяя слеши на дефисы)
    
    Args:
        path (str): Path проекта
        
    Returns:
        str: ID проекта
        
    Examples:
        >>> generate_id_from_path("exlibrus/frontend/components")
        'exlibrus-frontend-components'
    """
    return path.replace('/', '-')


def validate_path(path):
    """
    Проверяет корректность path проекта
    
    Args:
        path (str): Path для проверки
        
    Returns:
        bool: True если path корректный
        
    Raises:
        ValueError: Если path некорректный
    """
    if not path:
        raise ValueError("Path не может быть пустым")
    
    # Проверяем символы
    if not re.match(r'^[a-z0-9\-/]+$', path):
        raise ValueError("Path может содержать только латиницу, цифры, дефисы и слеши")
    
    # Проверяем что не начинается и не заканчивается слешем
    if path.startswith('/') or path.endswith('/'):
        raise ValueError("Path не должен начинаться или заканчиваться слешем")
    
    # Проверяем отсутствие множественных слешей
    if '//' in path:
        raise ValueError("Path не должен содержать множественные слеши")
    
    # Проверяем что каждый сегмент не пустой
    segments = path.split('/')
    for segment in segments:
        if not segment:
            raise ValueError("Сегменты path не могут быть пустыми")
        if segment.startswith('-') or segment.endswith('-'):
            raise ValueError("Сегменты path не должны начинаться или заканчиваться дефисом")
    
    return True


if __name__ == "__main__":
    # Тесты
    test_cases = [
        "ExLibrus",
        "Б24 Отчеты", 
        "React Components",
        "Настройки модуля",
        "API интеграция v2.0",
        "Frontend/Backend разработка"
    ]
    
    print("=== Тесты транслитерации ===")
    for test in test_cases:
        result = transliterate(test)
        print(f"'{test}' → '{result}'")
    
    print("\n=== Тесты генерации path ===")
    print(f"generate_path_from_title('Components') → '{generate_path_from_title('Components')}'")
    print(f"generate_path_from_title('Components', 'exlibrus/frontend') → '{generate_path_from_title('Components', 'exlibrus/frontend')}'")
    
    print("\n=== Тесты валидации ===")
    valid_paths = ["exlibrus", "exlibrus/frontend", "b24/aktiviti/otchety"]
    invalid_paths = ["/exlibrus", "exlibrus/", "ex//librus", "ex librus", "exlibrus/"]
    
    for path in valid_paths:
        try:
            validate_path(path)
            print(f"✓ '{path}' - корректный")
        except ValueError as e:
            print(f"✗ '{path}' - ошибка: {e}")
    
    for path in invalid_paths:
        try:
            validate_path(path)
            print(f"✗ '{path}' - должен быть некорректным!")
        except ValueError as e:
            print(f"✓ '{path}' - корректно отклонен: {e}")
