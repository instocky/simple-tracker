#!/usr/bin/env python3
"""
Быстрый трекер времени для планировщика
Версия с поддержкой иерархических проектов
"""
import datetime
import json
import os
import sys

# Импорт core модулей для работы с иерархией
try:
    from core.compatibility import detect_db_format, ensure_project_fields
    from core.hierarchy import update_aggregated_minutes, find_project_by_path
    from core.active import UserActivityMonitor, create_activity_monitor_from_config
    from core.notifications import show_break_notification, check_break_needed
    HIERARCHY_SUPPORT = True
    ACTIVITY_SUPPORT = True
    NOTIFICATION_SUPPORT = True
except ImportError:
    # Fallback если core модули недоступны
    HIERARCHY_SUPPORT = False
    ACTIVITY_SUPPORT = False
    NOTIFICATION_SUPPORT = False


def quick_track():
    """Быстрый трекинг без логирования в консоль"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, 'db.json')
        log_path = os.path.join(script_dir, 'tracker.log')
        
        # Загружаем данные
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Проверяем рабочее время (08:00-20:00)
        now = datetime.datetime.now()
        if now.hour < 8 or now.hour >= 20:
            return True  # Вне рабочих часов
        
        # Находим активный проект с поддержкой иерархии
        current_project = find_active_project(data)
        
        if not current_project:
            return False
        
        # Вычисляем позицию бита (каждые 5 минут с 08:00)
        start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
        time_diff = now - start_time
        total_minutes = int(time_diff.total_seconds() / 60)
        bit_position = total_minutes // 5
        
        if bit_position < 0 or bit_position >= 144:
            return True
        
        # Проверяем активность пользователя (Этап 1)
        should_track, activity_info = check_user_activity(data)
        
        # Логируем информацию об активности
        activity_entry = f"{now.strftime('%Y-%m-%d %H:%M:%S')} | ACTIVITY | Active: {activity_info['is_active']} | Idle: {activity_info['idle_seconds']}s | Level: {activity_info['activity_level']}"
        if activity_info.get('active_window'):
            activity_entry += f" | Window: '{activity_info['active_window']}'"
        activity_entry += "\n"
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(activity_entry)
        
        # Если пользователь неактивен, пропускаем запись времени
        if not should_track:
            skip_entry = f"{now.strftime('%Y-%m-%d %H:%M:%S')} | {current_project['title']} | BIT_SKIP | Position: {bit_position} | REASON: user_idle\n"
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(skip_entry)
            return True
        
        # Получаем текущую дату
        today = now.strftime("%Y-%m-%d")
        
        # Получаем маску (создаем если нет)
        if 'daily_masks' not in current_project:
            current_project['daily_masks'] = {}
        
        current_mask = current_project['daily_masks'].get(today, "0" * 144)
        if len(current_mask) < 144:
            current_mask = current_mask + "0" * (144 - len(current_mask))
        
        # Устанавливаем бит
        mask_list = list(current_mask)
        if mask_list[bit_position] == '0':
            mask_list[bit_position] = '1'
            new_mask = ''.join(mask_list)
            
            # Обновляем данные
            current_project['daily_masks'][today] = new_mask
            
            # Пересчитываем общее время проекта
            old_total_minutes = current_project.get('total_minutes', 0)
            new_total_minutes = 0
            for mask in current_project['daily_masks'].values():
                new_total_minutes += mask.count('1') * 5
            current_project['total_minutes'] = new_total_minutes
            
            # Обновляем aggregated_minutes в иерархии (если поддерживается)
            time_changed = old_total_minutes != new_total_minutes
            if time_changed and HIERARCHY_SUPPORT:
                update_hierarchy_minutes(current_project, data)
            
            # Проверяем нужен ли перерыв (новая функциональность)
            break_result = check_break_notification(current_project, data, now, log_path)
            
            # Сохраняем
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Пишем в лог с информацией об иерархии
            log_entry = create_log_entry(now, current_project, bit_position, time_changed)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        
        return True
        
    except Exception as e:
        # Записываем ошибку в лог для диагностики
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(script_dir, 'tracker.log')
            error_entry = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | ERROR | {str(e)}\n"
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(error_entry)
        except:
            pass
        return False


def find_active_project(data):
    """
    Находит активный проект с поддержкой совместимости форматов
    TODO: LEGACY_SUPPORT - генерирует поля на лету для старого формата
    """
    for project in data['projects']:
        if project.get('status') == 'active':
            # Если поддержка иерархии включена, обеспечиваем наличие всех полей
            if HIERARCHY_SUPPORT:
                # TODO: LEGACY_SUPPORT - удалить после миграции
                project = ensure_project_fields(project)
            return project
    return None


def update_hierarchy_minutes(current_project, data):
    """
    Обновляет aggregated_minutes в иерархии после изменения времени
    """
    try:
        if not HIERARCHY_SUPPORT:
            return
        
        # Получаем path проекта (с fallback для совместимости)
        project_path = current_project.get('path')
        if not project_path:
            # TODO: LEGACY_SUPPORT - генерируем path из title если отсутствует
            from core.transliteration import generate_path_from_title
            project_path = generate_path_from_title(current_project['title'])
            current_project['path'] = project_path
        
        # Обновляем aggregated_minutes для проекта и всех родителей
        updated_paths = update_aggregated_minutes(project_path, data['projects'])
        
        # Логируем обновления (для диагностики)
        if updated_paths:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(script_dir, 'tracker.log')
            now = datetime.datetime.now()
            hierarchy_entry = f"{now.strftime('%Y-%m-%d %H:%M:%S')} | HIERARCHY_UPDATE | Updated paths: {', '.join(updated_paths)}\n"
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(hierarchy_entry)
                
    except Exception as e:
        # Не прерываем работу трекера из-за ошибок в иерархии
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(script_dir, 'tracker.log')
        now = datetime.datetime.now()
        error_entry = f"{now.strftime('%Y-%m-%d %H:%M:%S')} | HIERARCHY_ERROR | {str(e)}\n"
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(error_entry)


def create_log_entry(now, project, bit_position, time_changed, reason="user_active"):
    """Создает запись лога с информацией о проекте и иерархии"""
    base_entry = f"{now.strftime('%Y-%m-%d %H:%M:%S')} | {project['title']} | BIT_SET | Position: {bit_position}"
    
    # Добавляем информацию об иерархии если поддерживается
    if HIERARCHY_SUPPORT and time_changed:
        total_mins = project.get('total_minutes', 0)
        aggregated_mins = project.get('aggregated_minutes', total_mins)
        project_path = project.get('path', 'unknown')
        
        base_entry += f" | Path: {project_path} | Total: {total_mins}min | Aggregated: {aggregated_mins}min"
    
    # Добавляем причину записи
    base_entry += f" | REASON: {reason}"
    
    return base_entry + "\n"


def check_break_notification(current_project, data, now, log_path):
    """
    Проверяет нужен ли перерыв и показывает уведомление
    Интеграция согласно specification_0607+.md
    
    Args:
        current_project (dict): Текущий активный проект
        data (dict): Данные БД
        now (datetime): Текущее время
        log_path (str): Путь к лог файлу
        
    Returns:
        dict: Информация о результате проверки перерыва
    """
    if not NOTIFICATION_SUPPORT:
        return {'break_needed': False, 'reason': 'notifications_disabled'}
    
    try:
        # Получаем настройки перерывов из meta (если есть)
        meta = data.get('meta', {})
        break_settings = meta.get('break_reminders', {})
        
        # Настройки по умолчанию (каждые 2 часа)
        break_interval_minutes = break_settings.get('interval_minutes', 120)
        enabled = break_settings.get('enabled', True)
        
        if not enabled:
            return {'break_needed': False, 'reason': 'breaks_disabled'}
        
        # Вычисляем время непрерывной работы
        continuous_work_minutes = get_continuous_work_minutes(current_project, now)
        
        # Проверяем нужен ли перерыв
        if check_break_needed(continuous_work_minutes, break_interval_minutes):
            # Показываем уведомление согласно specification_0607+.md
            action = show_break_notification(
                title="Время для перерыва!",
                message=f"Вы работаете уже {continuous_work_minutes} минут подряд.\nВыберите длительность перерыва:"
            )
            
            # Логируем результат
            log_entry = f"{now.strftime('%Y-%m-%d %H:%M:%S')} | BREAK_NOTIFICATION | Action: {action} | Work_minutes: {continuous_work_minutes}\n"
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            # Обрабатываем выбор пользователя согласно specification
            if action == "pause_5":
                handle_break_action(current_project, data, 5, log_path, now)
                return {'break_needed': True, 'action': 'pause_5', 'minutes': 5}
            elif action == "pause_15":
                handle_break_action(current_project, data, 15, log_path, now)
                return {'break_needed': True, 'action': 'pause_15', 'minutes': 15}
            elif action == "snooze":
                handle_snooze_action(current_project, data, log_path, now)
                return {'break_needed': True, 'action': 'snooze', 'snooze_minutes': 10}
            elif action == "cancelled":
                return {'break_needed': True, 'action': 'cancelled'}
            else:
                return {'break_needed': True, 'action': 'error'}
        
        return {'break_needed': False, 'continuous_minutes': continuous_work_minutes}
        
    except Exception as e:
        # Логируем ошибку но не прерываем работу трекера
        error_entry = f"{now.strftime('%Y-%m-%d %H:%M:%S')} | BREAK_CHECK_ERROR | {str(e)}\n"
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(error_entry)
        return {'break_needed': False, 'reason': 'error', 'error': str(e)}


def get_continuous_work_minutes(project, now):
    """
    Вычисляет количество минут непрерывной работы
    Упрощенная логика: считаем общее время проекта за сегодня
    """
    try:
        today = now.strftime("%Y-%m-%d")
        daily_masks = project.get('daily_masks', {})
        today_mask = daily_masks.get(today, "0" * 144)
        
        # Считаем активные биты (каждый бит = 5 минут)
        active_bits = today_mask.count('1')
        return active_bits * 5
    except:
        return 0


def handle_break_action(project, data, break_minutes, log_path, now):
    """
    Обрабатывает выбор перерыва пользователем
    
    Args:
        project (dict): Текущий проект  
        data (dict): Данные БД
        break_minutes (int): Длительность перерыва
        log_path (str): Путь к лог файлу
        now (datetime): Текущее время
    """
    try:
        # Логируем начало перерыва
        log_entry = f"{now.strftime('%Y-%m-%d %H:%M:%S')} | BREAK_START | Project: {project['title']} | Duration: {break_minutes}m\n"
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # TODO: Можно добавить логику паузы проекта или таймера перерыва
        # Пока просто логируем действие
        
    except Exception as e:
        error_entry = f"{now.strftime('%Y-%m-%d %H:%M:%S')} | BREAK_ACTION_ERROR | {str(e)}\n"
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(error_entry)


def handle_snooze_action(project, data, log_path, now):
    """
    Обрабатывает отложение перерыва
    
    Args:
        project (dict): Текущий проект
        data (dict): Данные БД  
        log_path (str): Путь к лог файлу
        now (datetime): Текущее время
    """
    try:
        # Логируем отложение перерыва
        log_entry = f"{now.strftime('%Y-%m-%d %H:%M:%S')} | BREAK_SNOOZE | Project: {project['title']} | Snoozed for: 10m\n"
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # TODO: Можно добавить логику отложения (например, запомнить время следующего напоминания)
        
    except Exception as e:
        error_entry = f"{now.strftime('%Y-%m-%d %H:%M:%S')} | SNOOZE_ACTION_ERROR | {str(e)}\n"
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(error_entry)


def check_user_activity(data):
    """
    Проверяет активность пользователя и определяет нужно ли записывать время
    
    Args:
        data (dict): Данные из db.json для получения настроек
        
    Returns:
        tuple: (should_track: bool, activity_info: dict)
    """
    if not ACTIVITY_SUPPORT:
        # Если модуль активности недоступен, считаем пользователя активным
        return True, {
            'is_active': True,
            'idle_seconds': 0.0,
            'activity_level': 'active',
            'error': 'activity_support_disabled'
        }
    
    try:
        # Создаем монитор активности с настройками из БД
        activity_monitor = create_activity_monitor_from_config(data)
        
        # Получаем информацию об активности
        activity_info = activity_monitor.get_full_activity_report()
        
        # Определяем нужно ли записывать время
        should_track = activity_info['is_active']
        
        return should_track, activity_info
        
    except Exception as e:
        # В случае ошибки считаем пользователя активным (безопасное поведение)
        return True, {
            'is_active': True,
            'idle_seconds': 0.0,
            'activity_level': 'active',
            'error': str(e)
        }


def get_db_format_info():
    """
    Возвращает информацию о формате БД для диагностики
    Используется в тестах и отладке
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, 'db.json')
        
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if HIERARCHY_SUPPORT:
            db_format = detect_db_format(data)
            return {
                'format': db_format,
                'hierarchy_support': True,
                'projects_count': len(data.get('projects', []))
            }
        else:
            return {
                'format': 'unknown',
                'hierarchy_support': False,
                'projects_count': len(data.get('projects', []))
            }
    except:
        return {
            'format': 'error',
            'hierarchy_support': HIERARCHY_SUPPORT,
            'projects_count': 0
        }


if __name__ == "__main__":
    success = quick_track()
    sys.exit(0 if success else 1)
