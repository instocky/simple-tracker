#!/usr/bin/env python3
"""
Запуск всех тестов Simple Time Tracker
"""
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_core import main as test_core_main
from tests.test_tracker import main as test_tracker_main
from tests.test_project_manager import main as test_project_manager_main


def run_all_tests():
    """Запускает все доступные тесты"""
    print("Запуск всех тестов Simple Time Tracker")
    print("=" * 60)
    
    try:
        # Тесты core модулей (готовы)
        test_core_main()
        print()
        
        # Тесты tracker_quick (TODO)
        test_tracker_main() 
        print()
        
        # Тесты project_manager (TODO)
        test_project_manager_main()
        
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
