#!/usr/bin/env python3
"""
Исправление Unicode символов в проекте
Замена на ASCII-совместимые аналоги
"""
import os
import re

def fix_unicode_in_files():
    """Исправляет Unicode символы во всех файлах проекта"""
    
    # Таблица замен
    unicode_replacements = {
        '✓': '[OK]',
        '✗': '[FAIL]', 
        '🚀': '',
        '│': '|',
        '├──': '+-',
        '├── ': '+- ',
        '→': '->',
        '←': '<-',
        '↑': '^',
        '↓': 'v'
    }
    
    # Файлы для обработки
    files_to_fix = [
        'core/transliteration.py',
        'project_manager.py', 
        'tests/test_project_manager_simple.py',
        'tests/test_project_manager_new.py',
        'tests/test_project_manager.py'
    ]
    
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    for file_path in files_to_fix:
        full_path = os.path.join(script_dir, file_path)
        
        if os.path.exists(full_path):
            print(f"Исправляем: {file_path}")
            
            # Читаем файл
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Применяем замены
            modified = False
            for unicode_char, ascii_replacement in unicode_replacements.items():
                if unicode_char in content:
                    content = content.replace(unicode_char, ascii_replacement)
                    modified = True
                    print(f"  {unicode_char} -> {ascii_replacement}")
            
            # Сохраняем если были изменения
            if modified:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  Файл обновлен")
            else:
                print(f"  Изменений не требуется")
        else:
            print(f"Файл не найден: {file_path}")


def test_console_output():
    """Тестирует вывод в консоль после исправлений"""
    print("\n=== Тест консольного вывода ===")
    
    test_strings = [
        "Тест ASCII: [OK] [FAIL]",
        "Дерево: +- Ветка", 
        "Стрелка: ->",
        "Результат: [OK]"
    ]
    
    for test_str in test_strings:
        try:
            print(f"  {test_str}")
        except UnicodeEncodeError as e:
            print(f"  ОШИБКА: {e}")


if __name__ == "__main__":
    print("Исправление Unicode символов для Windows консоли")
    print("=" * 60)
    
    fix_unicode_in_files()
    test_console_output()
    
    print("=" * 60)
    print("Исправление завершено!")
