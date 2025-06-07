#!/usr/bin/env python3
"""
Утилита для безопасного вывода в Windows консоль
"""
import sys


def safe_print(*args, **kwargs):
    """
    Безопасная печать с автоматической заменой Unicode символов
    """
    # Таблица замен проблемных символов
    unicode_map = {
        '✓': '[OK]',
        '✗': '[FAIL]',
        '🚀': '',
        '│': '|',
        '├': '+',
        '──': '--',
        '→': '->',
        '←': '<-',
        '↑': '^',
        '↓': 'v'
    }
    
    # Обрабатываем все аргументы
    safe_args = []
    for arg in args:
        if isinstance(arg, str):
            safe_arg = arg
            for unicode_char, replacement in unicode_map.items():
                safe_arg = safe_arg.replace(unicode_char, replacement)
            safe_args.append(safe_arg)
        else:
            safe_args.append(arg)
    
    # Выводим с обработкой ошибок
    try:
        print(*safe_args, **kwargs)
    except UnicodeEncodeError:
        # Если все еще есть проблемы, используем ASCII-only
        ascii_args = []
        for arg in safe_args:
            if isinstance(arg, str):
                ascii_args.append(arg.encode('ascii', 'replace').decode('ascii'))
            else:
                ascii_args.append(str(arg))
        print(*ascii_args, **kwargs)


def get_safe_symbols():
    """Возвращает словарь безопасных символов для консоли"""
    return {
        'check': '[OK]',
        'cross': '[FAIL]', 
        'tree_vertical': '|',
        'tree_branch': '+-',
        'arrow_right': '->',
        'arrow_left': '<-',
        'status_active': '[АКТИВЕН]',
        'status_paused': '[пауза]',
        'status_completed': '[завершен]',
        'status_archived': '[архив]'
    }


def format_tree_line(title, status, level=0):
    """Форматирует строку для древовидного отображения"""
    symbols = get_safe_symbols()
    
    # Отступ по уровню
    if level == 0:
        prefix = ""
    else:
        prefix = "  " * (level - 1) + "+-"
    
    # Статус в скобках
    status_map = {
        'active': symbols['status_active'],
        'paused': symbols['status_paused'],
        'completed': symbols['status_completed'], 
        'archived': symbols['status_archived']
    }
    
    status_text = status_map.get(status, f'[{status}]')
    
    return f"{prefix}{title} {status_text}"


def format_time_display(total_minutes, aggregated_minutes=None):
    """Форматирует отображение времени"""
    hours, mins = divmod(total_minutes, 60)
    time_str = f"{hours}ч{mins}м"
    
    if aggregated_minutes is not None and aggregated_minutes != total_minutes:
        agg_hours, agg_mins = divmod(aggregated_minutes, 60)
        time_str += f" / {agg_hours}ч{agg_mins}м"
    
    return time_str


if __name__ == "__main__":
    # Тестирование
    print("=== Тест безопасного вывода ===")
    
    # Проблемные символы
    safe_print("Тест символов:", "check", "[OK]", "cross", "[FAIL]")
    
    # Форматирование дерева
    tree_lines = [
        format_tree_line("ExLibrus", "active", 0),
        format_tree_line("Frontend", "paused", 1),
        format_tree_line("Components", "paused", 2)
    ]
    
    for line in tree_lines:
        safe_print(line)
    
    # Форматирование времени
    safe_print("Время:", format_time_display(125, 185))
    
    print("=== Тест завершен ===")
