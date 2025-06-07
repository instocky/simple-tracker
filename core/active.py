#!/usr/bin/env python3
"""
core/active.py - Отслеживание активности пользователя Windows
Этап 1: Базовая проверка активности через Windows API
"""
import ctypes
import time
import json
from datetime import datetime
from ctypes import wintypes


class LASTINPUTINFO(ctypes.Structure):
    """Структура для GetLastInputInfo Windows API"""
    _fields_ = [
        ('cbSize', wintypes.UINT),
        ('dwTime', wintypes.DWORD)
    ]


class UserActivityMonitor:
    """Монитор активности пользователя Windows"""
    
    def __init__(self, idle_threshold_seconds=300):
        """
        Инициализация монитора активности
        
        Args:
            idle_threshold_seconds (int): Порог бездействия в секундах (по умолчанию 5 минут)
        """
        self.idle_threshold = idle_threshold_seconds
        
    def get_idle_time(self):
        """
        Получает время бездействия пользователя в секундах
        
        Returns:
            float: Время бездействия в секундах
        """
        try:
            # Создаем структуру для API вызова
            lii = LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
            
            # Вызываем Windows API
            result = ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
            
            if not result:
                # Если API вызов неудачен, возвращаем 0 (считаем пользователя активным)
                return 0.0
            
            # Получаем текущее время системы
            current_time = ctypes.windll.kernel32.GetTickCount()
            
            # Вычисляем время бездействия
            idle_time_ms = current_time - lii.dwTime
            idle_time_seconds = idle_time_ms / 1000.0
            
            # Защита от отрицательных значений (может происходить при переполнении)
            return max(0.0, idle_time_seconds)
            
        except Exception as e:
            # В случае ошибки считаем пользователя активным
            return 0.0
    
    def get_active_window_title(self):
        """
        Получает заголовок активного окна
        
        Returns:
            str: Заголовок активного окна или пустую строку при ошибке
        """
        try:
            # Получаем handle активного окна
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            
            if not hwnd:
                return ""
            
            # Получаем длину заголовка
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            
            if length == 0:
                return ""
            
            # Создаем буфер и получаем заголовок
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            
            return buff.value or ""
            
        except Exception as e:
            return ""
    
    def is_user_active(self):
        """
        Определяет активен ли пользователь
        
        Returns:
            bool: True если пользователь активен, False если бездействует
        """
        idle_time = self.get_idle_time()
        return idle_time < self.idle_threshold
    
    def get_activity_status(self):
        """
        Получает детальный статус активности
        
        Returns:
            dict: Словарь с информацией об активности
        """
        idle_time = self.get_idle_time()
        is_active = idle_time < self.idle_threshold
        
        return {
            'is_active': is_active,
            'idle_seconds': round(idle_time, 1),
            'threshold_seconds': self.idle_threshold,
            'activity_level': self._get_activity_level(idle_time)
        }
    
    def get_full_activity_report(self):
        """
        Получает полный отчет об активности пользователя
        
        Returns:
            dict: Полный отчет с timestamp, активностью и активным окном
        """
        idle_time = self.get_idle_time()
        is_active = idle_time < self.idle_threshold
        active_window = self.get_active_window_title()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'is_active': is_active,
            'idle_seconds': round(idle_time, 1),
            'threshold_seconds': self.idle_threshold,
            'activity_level': self._get_activity_level(idle_time),
            'active_window': active_window,
            'window_available': bool(active_window)
        }
    
    def _get_activity_level(self, idle_time):
        """
        Определяет уровень активности на основе времени бездействия
        
        Args:
            idle_time (float): Время бездействия в секундах
            
        Returns:
            str: Уровень активности ('active', 'idle', 'away')
        """
        if idle_time < 30:  # Менее 30 секунд
            return 'active'
        elif idle_time < self.idle_threshold:  # Менее порога
            return 'idle'
        else:  # Больше порога
            return 'away'


def create_activity_monitor_from_config(config_data):
    """
    Создает монитор активности на основе конфигурации
    
    Args:
        config_data (dict): Данные конфигурации из db.json
        
    Returns:
        UserActivityMonitor: Настроенный монитор активности
    """
    # Получаем настройки из meta секции
    meta = config_data.get('meta', {})
    activity_config = meta.get('activity_monitoring', {})
    
    # Используем значение из конфигурации или значение по умолчанию
    idle_threshold = activity_config.get('idle_threshold_seconds', 300)
    
    return UserActivityMonitor(idle_threshold_seconds=idle_threshold)


def test_activity_monitor():
    """Тестирует работу монитора активности"""
    print("=== Тест монитора активности ===")
    
    monitor = UserActivityMonitor(idle_threshold_seconds=300)
    
    # Тест базовых функций
    idle_time = monitor.get_idle_time()
    is_active = monitor.is_user_active()
    window_title = monitor.get_active_window_title()
    
    print(f"Время бездействия: {idle_time:.1f} секунд")
    print(f"Пользователь активен: {is_active}")
    print(f"Активное окно: '{window_title}'")
    
    # Тест полного отчета
    report = monitor.get_full_activity_report()
    print(f"\nПолный отчет:")
    for key, value in report.items():
        print(f"  {key}: {value}")
    
    return report


def main():
    """Основная функция для запуска как отдельного скрипта"""
    try:
        monitor = UserActivityMonitor()
        report = monitor.get_full_activity_report()
        
        # Выводим результат в JSON формате для использования другими скриптами
        print(json.dumps(report, ensure_ascii=False, indent=2))
        
        return True
        
    except Exception as e:
        # В случае ошибки возвращаем базовый активный статус
        error_report = {
            'timestamp': datetime.now().isoformat(),
            'is_active': True,  # По умолчанию считаем активным
            'idle_seconds': 0.0,
            'threshold_seconds': 300,
            'activity_level': 'active',
            'active_window': '',
            'window_available': False,
            'error': str(e)
        }
        
        print(json.dumps(error_report, ensure_ascii=False, indent=2))
        return False


if __name__ == "__main__":
    # Если запускается как скрипт, выполняем тест или основную функцию
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_activity_monitor()
    else:
        main()
