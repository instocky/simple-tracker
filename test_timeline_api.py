#!/usr/bin/env python3
"""
Тест для API endpoint /api/timeline/data
Проверяет правильность работы нового функционала
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_server import calculate_hourly_timeline_data, get_passive_tracking_data_for_date
import project_manager
import json

def test_calculate_hourly_timeline_data():
    """Тест функции вычисления почасовых данных"""
    print("=== Тест calculate_hourly_timeline_data ===")
    
    # Тестовые данные для одного дня
    test_daily_masks = {
        'computer_activity': '1' * 72 + '0' * 72,  # Активность только утром (8-14)
        'project_activity': '1' * 36 + '0' * 108,  # Проектная работа только утром (8-11)
        'idle_periods': '0' * 72 + '1' * 72,       # Простой после обеда
        'untracked_work': '0' * 144
    }
    
    result = calculate_hourly_timeline_data('2025-11-27', test_daily_masks)
    
    print(f"Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # Проверяем структуру
    assert result['success'] == True
    assert result['date'] == '2025-11-27'
    assert 'total_active_minutes' in result
    assert 'hourly_data' in result
    assert len(result['hourly_data']) == 12  # 12 часов с 08:00 до 19:00
    
    # Проверяем первые несколько часов
    for i, hour_data in enumerate(result['hourly_data'][:6]):  # Первые 6 часов
        expected_time = f"{8+i:02d}:00"
        assert hour_data['hour'] == expected_time
        assert hour_data['total_minutes'] == 60
        
        # Утром должна быть активность
        if i < 6:  # 8-14
            assert hour_data['active_minutes'] > 0
            assert hour_data['status'] in ['low', 'medium', 'high']
        else:
            assert hour_data['active_minutes'] == 0
            assert hour_data['status'] == 'idle'
    
    print("✅ Тест calculate_hourly_timeline_data пройден")


def test_get_passive_tracking_data():
    """Тест получения данных пассивного отслеживания"""
    print("\n=== Тест get_passive_tracking_data_for_date ===")
    
    try:
        # Загружаем реальную БД
        data, _ = project_manager.load_db()
        
        # Ищем доступные даты
        passive = data.get('meta', {}).get('passive_tracking', {})
        if 'daily_masks' in passive and passive['daily_masks']:
            available_dates = list(passive['daily_masks'].keys())
            print(f"Доступные даты в БД: {available_dates}")
            
            # Тестируем на первой доступной дате
            test_date = available_dates[0]
            result = get_passive_tracking_data_for_date(data, test_date)
            
            if result:
                print(f"✅ Найдены данные за {test_date}")
                print(f"Доступные маски: {list(result.keys())}")
            else:
                print(f"❌ Данные за {test_date} не найдены")
        else:
            print("⚠️  Данные пассивного отслеживания не найдены в БД")
            
    except Exception as e:
        print(f"❌ Ошибка при работе с БД: {e}")


def test_api_endpoint_simulation():
    """Симуляция работы API endpoint"""
    print("\n=== Симуляция API endpoint ===")
    
    try:
        # Загружаем БД
        data, _ = project_manager.load_db()
        test_date = '2025-11-27'  # Тестовая дата
        
        # Получаем данные
        daily_masks = get_passive_tracking_data_for_date(data, test_date)
        
        if daily_masks is None:
            print(f"⚠️  Нет данных за {test_date}, возвращаем пустую структуру")
            daily_masks = {
                'computer_activity': '',
                'project_activity': '',
                'idle_periods': '',
                'untracked_work': ''
            }
        
        # Вычисляем результат
        result = calculate_hourly_timeline_data(test_date, daily_masks)
        
        print(f"Результат API для {test_date}:")
        print(f"- Успех: {result['success']}")
        print(f"- Дата: {result['date']}")
        print(f"- Общие активные минуты: {result['total_active_minutes']}")
        print(f"- Количество часовых слотов: {len(result['hourly_data'])}")
        
        # Показываем первые несколько слотов
        print("\nПервые 6 часовых слотов:")
        for hour_data in result['hourly_data'][:6]:
            print(f"  {hour_data['hour']}: {hour_data['active_minutes']} мин ({hour_data['status']})")
        
        print("✅ API endpoint симуляция завершена")
        
    except Exception as e:
        print(f"❌ Ошибка симуляции API: {e}")


def main():
    """Основная функция тестирования"""
    print("Запуск тестов для /api/timeline/data")
    print("=" * 50)
    
    try:
        test_calculate_hourly_timeline_data()
        test_get_passive_tracking_data()
        test_api_endpoint_simulation()
        
        print("\n" + "=" * 50)
        print("🎉 Все тесты завершены!")
        print("\nИнформация о новом endpoint:")
        print("- URL: GET /api/timeline/data")
        print("- Параметр: date=YYYY-MM-DD (обязательный)")
        print("- Формат ответа: JSON со структурированными данными")
        print("- Диапазон времени: 08:00-19:00 (12 часов)")
        
    except Exception as e:
        print(f"\n❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()