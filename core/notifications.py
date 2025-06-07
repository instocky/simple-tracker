"""
Модуль для показа уведомлений с кнопками
Интегрирован в Simple Time Tracker для замены Toast уведомлений

Использование согласно specification_0607+.md:
    from core.notifications import show_break_notification
    action = show_break_notification("Перерыв!", "Время отдохнуть")
    if action == "pause_5":
        start_break(5)
"""

import tkinter as tk
from tkinter import ttk
import threading
import time

def show_break_notification(title="Время для перерыва!", message="Вы работаете уже долго. Сделайте перерыв."):
    """
    Показать уведомление о перерыве с кнопками
    
    Args:
        title (str): Заголовок уведомления
        message (str): Текст сообщения
        
    Returns:
        str: "pause_5", "pause_15", "snooze", "cancelled" или None при ошибке
        
    Согласно specification_0607+.md:
    - "pause_5": Выбран 5-минутный перерыв
    - "pause_15": Выбран 15-минутный перерыв  
    - "snooze": Перерыв отложен
    - "cancelled": Окно закрыто без выбора
    """
    result = {"action": None}
    
    def create_dialog():
        try:
            # Создаем главное окно
            root = tk.Tk()
            root.title(title)
            root.geometry("500x280")
            root.resizable(False, False)
            
            # Центрируем окно на экране
            root.eval('tk::PlaceWindow . center')
            
            # Устанавливаем современную тему
            style = ttk.Style()
            try:
                style.theme_use('vista')  # Современная тема для Windows
            except:
                style.theme_use('default')
            
            # Настраиваем цвета
            root.configure(bg='#f0f0f0')
            
            # Основной контейнер
            main_frame = ttk.Frame(root, padding="30")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Заголовок
            title_label = ttk.Label(
                main_frame, 
                text=title,
                font=('Segoe UI', 16, 'bold'),
                foreground='#2c3e50'
            )
            title_label.pack(pady=(0, 15))
            
            # Сообщение
            message_label = ttk.Label(
                main_frame,
                text=message,
                font=('Segoe UI', 11),
                foreground='#34495e',
                wraplength=450,
                justify='center'
            )
            message_label.pack(pady=(0, 25))
            
            # Контейнер для кнопок
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(pady=(10, 0))
            
            # Функции для обработки кнопок
            def on_pause_5():
                result["action"] = "pause_5"
                root.destroy()
            
            def on_pause_15():
                result["action"] = "pause_15"
                root.destroy()
            
            def on_snooze():
                result["action"] = "snooze"
                root.destroy()
            
            def on_close():
                result["action"] = "cancelled"
                root.destroy()
            
            # Создаем кнопки с современным дизайном
            btn_5min = ttk.Button(
                button_frame,
                text="⏰ 5 минут",
                command=on_pause_5,
                width=15
            )
            btn_5min.pack(side=tk.LEFT, padx=10)
            
            btn_15min = ttk.Button(
                button_frame,
                text="☕ 15 минут", 
                command=on_pause_15,
                width=15
            )
            btn_15min.pack(side=tk.LEFT, padx=10)
            
            btn_snooze = ttk.Button(
                button_frame,
                text="⏱️ Отложить",
                command=on_snooze,
                width=15
            )
            btn_snooze.pack(side=tk.LEFT, padx=10)
            
            # Обработка закрытия окна
            root.protocol("WM_DELETE_WINDOW", on_close)
            
            # Делаем окно поверх всех остальных
            root.attributes('-topmost', True)
            root.lift()
            root.focus_force()
            
            # Фокус на первую кнопку
            btn_5min.focus()
            
            # Запускаем главный цикл
            root.mainloop()
            
        except Exception as e:
            # В случае ошибки Tkinter возвращаем None
            result["action"] = None
    
    # Запускаем диалог в основном потоке
    create_dialog()
    
    return result["action"]

def show_simple_notification(title, message, buttons=None):
    """
    Универсальная функция для показа уведомлений
    
    Args:
        title (str): Заголовок
        message (str): Сообщение
        buttons (list): Список словарей [{"text": "Кнопка", "value": "значение"}]
        
    Returns:
        str: Значение нажатой кнопки или "cancelled"
    """
    if not buttons:
        buttons = [{"text": "OK", "value": "ok"}]
    
    result = {"action": None}
    
    def create_dialog():
        try:
            root = tk.Tk()
            root.title(title)
            
            # Рассчитываем размер окна в зависимости от количества кнопок
            width = max(400, len(buttons) * 120 + 100)
            root.geometry(f"{width}x200")
            root.resizable(False, False)
            root.eval('tk::PlaceWindow . center')
            
            style = ttk.Style()
            try:
                style.theme_use('vista')
            except:
                style.theme_use('default')
            
            main_frame = ttk.Frame(root, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Заголовок
            ttk.Label(main_frame, text=title, font=('Segoe UI', 14, 'bold')).pack(pady=(0, 10))
            
            # Сообщение
            ttk.Label(main_frame, text=message, font=('Segoe UI', 10), 
                     wraplength=width-40, justify='center').pack(pady=(0, 20))
            
            # Кнопки
            button_frame = ttk.Frame(main_frame)
            button_frame.pack()
            
            def button_clicked(value):
                result["action"] = value
                root.destroy()
            
            for button in buttons:
                btn = ttk.Button(button_frame, text=button["text"],
                               command=lambda v=button["value"]: button_clicked(v),
                               width=12)
                btn.pack(side=tk.LEFT, padx=5)
            
            root.protocol("WM_DELETE_WINDOW", lambda: button_clicked("cancelled"))
            root.attributes('-topmost', True)
            root.focus_force()
            
            root.mainloop()
            
        except Exception as e:
            result["action"] = "cancelled"
    
    create_dialog()
    return result["action"]


# Функции для интеграции с трекером времени (для будущего использования)
def check_break_needed(work_minutes, break_interval_minutes=120):
    """
    Проверяет, нужен ли перерыв
    
    Args:
        work_minutes (int): Количество минут непрерывной работы
        break_interval_minutes (int): Интервал для напоминания о перерыве (по умолчанию 2 часа)
        
    Returns:
        bool: True если пора делать перерыв
    """
    return work_minutes >= break_interval_minutes

def suggest_break_interactive():
    """
    Интерактивное предложение перерыва
    Возвращает выбранное действие пользователя
    """
    return show_break_notification(
        title="Время для перерыва!",
        message="Вы работаете уже долго.\nВыберите длительность перерыва или отложите напоминание:"
    )


if __name__ == '__main__':
    """Демо для тестирования уведомлений"""
    print("Тест уведомлений Simple Time Tracker")
    print("=" * 50)
    
    # Тест уведомления о перерыве
    print("Тестируем уведомление о перерыве...")
    action = show_break_notification()
    print(f"Выбранное действие: {action}")
    
    # Обработка согласно specification
    if action == "pause_5":
        print("Пользователь выбрал перерыв 5 минут")
    elif action == "pause_15":
        print("Пользователь выбрал перерыв 15 минут")
    elif action == "snooze":
        print("Пользователь отложил перерыв на 10 минут")
    elif action == "cancelled":
        print("Пользователь закрыл окно без выбора")
    elif action is None:
        print("Ошибка выполнения")
    
    print("\nТест завершен!")
