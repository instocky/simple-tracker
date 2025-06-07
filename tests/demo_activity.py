#!/usr/bin/env python3
"""
Демонстрация работы системы активности с разными порогами
"""
import sys
import os
import json

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.active import UserActivityMonitor
import tracker_quick


def demo_activity_thresholds():
    """Демонстрирует работу с разными порогами активности"""
    print("=== Демонстрация порогов активности ===")
    
    thresholds = [30, 60, 120, 300]  # 30с, 1мин, 2мин, 5мин
    
    for threshold in thresholds:
        monitor = UserActivityMonitor(idle_threshold_seconds=threshold)
        report = monitor.get_activity_status()
        
        print(f"\nПорог {threshold}с:")
        print(f"  Бездействие: {report['idle_seconds']}с")
        print(f"  Активен: {report['is_active']}")
        print(f"  Уровень: {report['activity_level']}")


def demo_tracker_decision():
    """Демонстрирует логику принятия решения трекером"""
    print("\n=== Демонстрация логики трекера ===")
    
    # Загружаем конфигурацию
    with open('db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Проверяем решение трекера
    should_track, activity_info = tracker_quick.check_user_activity(data)
    
    print(f"Конфигурация:")
    config = data['meta']['activity_monitoring']
    print(f"  Порог в БД: {config['idle_threshold_seconds']}с")
    print(f"  Включено: {config['enabled']}")
    
    print(f"\nТекущее состояние:")
    print(f"  Бездействие: {activity_info['idle_seconds']}с")
    print(f"  Активен: {activity_info['is_active']}")
    print(f"  Уровень: {activity_info['activity_level']}")
    
    print(f"\nРешение трекера:")
    print(f"  Записывать время: {should_track}")
    print(f"  Причина: {'user_active' if should_track else 'user_idle'}")
    
    # Симуляция с разными порогами
    print(f"\nСимуляция с другими порогами:")
    test_thresholds = [30, 60, 120]
    
    for threshold in test_thresholds:
        monitor = UserActivityMonitor(idle_threshold_seconds=threshold)
        is_active = monitor.is_user_active()
        idle_time = monitor.get_idle_time()
        
        decision = "ЗАПИСАТЬ" if is_active else "ПРОПУСТИТЬ"
        print(f"  Порог {threshold}с: {decision} (бездействие {idle_time:.1f}с)")


def demo_log_entries():
    """Демонстрирует как будут выглядеть записи в логе"""
    print("\n=== Демонстрация записей лога ===")
    
    from datetime import datetime
    now = datetime.now()
    
    # Симулируем разные сценарии
    scenarios = [
        {
            'name': 'Пользователь активен',
            'is_active': True,
            'idle_seconds': 45.2,
            'activity_level': 'active',
            'window': 'VS Code - project.py'
        },
        {
            'name': 'Пользователь в режиме ожидания',
            'is_active': True,
            'idle_seconds': 150.0,
            'activity_level': 'idle',
            'window': 'Chrome - GitHub'
        },
        {
            'name': 'Пользователь отошел',
            'is_active': False,
            'idle_seconds': 450.0,
            'activity_level': 'away',
            'window': 'Lock Screen'
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        
        # Лог активности
        activity_log = f"{now.strftime('%Y-%m-%d %H:%M:%S')} | ACTIVITY | Active: {scenario['is_active']} | Idle: {scenario['idle_seconds']}s | Level: {scenario['activity_level']} | Window: '{scenario['window']}'"
        print(f"  {activity_log}")
        
        # Лог трекинга
        if scenario['is_active']:
            track_log = f"{now.strftime('%Y-%m-%d %H:%M:%S')} | 0604_simple-tracker | BIT_SET | Position: 25 | REASON: user_active"
        else:
            track_log = f"{now.strftime('%Y-%m-%d %H:%M:%S')} | 0604_simple-tracker | BIT_SKIP | Position: 25 | REASON: user_idle"
        
        print(f"  {track_log}")


def main():
    """Основная демонстрация"""
    print("Демонстрация системы отслеживания активности")
    print("=" * 60)
    
    demo_activity_thresholds()
    demo_tracker_decision()
    demo_log_entries()
    
    print("=" * 60)
    print("Демонстрация завершена!")


if __name__ == "__main__":
    main()
