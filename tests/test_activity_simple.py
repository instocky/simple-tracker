#!/usr/bin/env python3
"""
Тест интеграции системы отслеживания активности
"""
import sys
import os
import json
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.active import UserActivityMonitor
import tracker_quick


def test_activity_integration():
    """Тестирует интеграцию активности с трекером"""
    print("=== Тест интеграции системы активности ===")
    
    # Тест 1: Проверка импортов
    print(f"Поддержка иерархии: {tracker_quick.HIERARCHY_SUPPORT}")
    print(f"Поддержка активности: {tracker_quick.ACTIVITY_SUPPORT}")
    
    # Тест 2: Загрузка конфигурации
    with open('db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    has_activity_config = 'activity_monitoring' in data.get('meta', {})
    print(f"Конфигурация активности в БД: {'ОК' if has_activity_config else 'ОТСУТСТВУЕТ'}")
    
    if has_activity_config:
        config = data['meta']['activity_monitoring']
        print(f"  Включено: {config.get('enabled', False)}")
        print(f"  Порог бездействия: {config.get('idle_threshold_seconds', 300)}с")
        print(f"  Отслеживание окон: {config.get('track_window_titles', False)}")
    
    # Тест 3: Функция проверки активности
    try:
        should_track, activity_info = tracker_quick.check_user_activity(data)
        print(f"\nПроверка активности:")
        print(f"  Нужно отслеживать: {should_track}")
        print(f"  Пользователь активен: {activity_info['is_active']}")
        print(f"  Время бездействия: {activity_info['idle_seconds']}с")
        print(f"  Уровень активности: {activity_info['activity_level']}")
        
        if 'active_window' in activity_info:
            print(f"  Активное окно: '{activity_info['active_window']}'")
        
        if 'error' in activity_info:
            print(f"  Ошибка: {activity_info['error']}")
            
    except Exception as e:
        print(f"\nОшибка при проверке активности: {e}")
    
    return True


def test_log_format():
    """Тестирует формат логирования активности"""
    print("\n=== Тест формата логов ===")
    
    # Читаем последние записи лога
    try:
        with open('tracker.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Ищем записи об активности
        activity_lines = [line for line in lines[-10:] if 'ACTIVITY' in line]
        
        print(f"Найдено записей активности: {len(activity_lines)}")
        
        for line in activity_lines[-3:]:  # Показываем последние 3
            print(f"  {line.strip()}")
        
        # Ищем записи BIT_SET или BIT_SKIP
        bit_lines = [line for line in lines[-10:] if ('BIT_SET' in line or 'BIT_SKIP' in line)]
        
        print(f"\nНайдено записей трекинга: {len(bit_lines)}")
        
        for line in bit_lines[-3:]:  # Показываем последние 3
            print(f"  {line.strip()}")
            
    except Exception as e:
        print(f"Ошибка чтения лога: {e}")


def main():
    """Основной тест"""
    print("Тестирование интеграции системы отслеживания активности")
    print("=" * 70)
    
    test_activity_integration()
    test_log_format()
    
    print("=" * 70)
    print("Тестирование завершено!")


if __name__ == "__main__":
    main()
