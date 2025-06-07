        if active_project_before:
            minutes_before = active_project_before.get('total_minutes', 0)
            print(f"Активный проект: {active_project_before['title']}")
            print(f"Время до: {minutes_before} минут")
            
            # Запускаем трекер
            print("Запуск tracker_quick.py...")
            result = tracker_quick.quick_track()
            print(f"Результат трекера: {result}")
            
            # Проверяем состояние после
            with open('db.json', 'r', encoding='utf-8') as f:
                data_after = json.load(f)
            
            active_project_after = None
            for project in data_after['projects']:
                if project['title'] == active_project_before['title']:
                    active_project_after = project
                    break
            
            if active_project_after:
                minutes_after = active_project_after.get('total_minutes', 0)
                print(f"Время после: {minutes_after} минут")
                print(f"Изменение: {minutes_after - minutes_before} минут")
                
                if minutes_after > minutes_before:
                    print("✓ Время записано (пользователь был активен)")
                else:
                    print("- Время не записано (пользователь был неактивен или вне рабочих часов)")
            
        else:
            print("Активный проект не найден")
            
    except Exception as e:
        print(f"Ошибка тестирования трекера: {e}")


def main():
    """Основной тест"""
    print("Тестирование интеграции системы отслеживания активности")
    print("=" * 70)
    
    test_activity_integration()
    test_log_format()
    test_tracker_with_activity()
    
    print("=" * 70)
    print("Тестирование завершено!")


if __name__ == "__main__":
    main()
