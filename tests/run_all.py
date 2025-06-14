#!/usr/bin/env python3
"""
Запуск всех тестов Simple Time Tracker
"""
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_core import main as test_core_main
from tests.test_tracker_new import main as test_tracker_new_main
from tests.test_project_manager_simple import main as test_project_manager_main
from tests.test_integration_final import main as test_integration_main


def run_all_tests():
    """Запускает все доступные тесты"""
    print("Запуск всех тестов Simple Time Tracker")
    print("=" * 60)
    
    try:
        # Тесты core модулей
        print("1. Тестирование core модулей...")
        test_core_main()
        print()
        
        # Тесты модифицированного tracker_quick
        print("2. Тестирование tracker_quick...")
        test_tracker_new_main()
        print()
        
        # Тесты project_manager
        print("3. Тестирование project_manager...")
        test_project_manager_main()
        print()
        
        # Тесты интеграции уведомлений
        print("4. Тестирование интеграции уведомлений...")
        test_integration_main()
        
        print("=" * 60)
        print("Все тесты завершены успешно!")
        
    except Exception as e:
        print(f"ОШИБКА в тестах: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
