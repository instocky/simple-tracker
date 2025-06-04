#!/usr/bin/env python3
import datetime
import random
import string
import os

def generate_random_text(length=10):
    """Генерирует случайный текст заданной длины"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def write_to_log():
    """Записывает строку с текущим временем и случайным текстом в лог файл"""
    # Получаем директорию, где находится скрипт
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_dir, 'data-2.log')
    
    # Получаем текущее время в нужном формате
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Генерируем случайный текст
    random_text = generate_random_text()
    
    # Формируем строку для записи
    log_entry = f"[{current_time}] Random text: {random_text}\n"
    
    try:
        # Записываем в файл (режим 'a' для добавления)
        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry)
        
        print(f"Записано в лог: {log_entry.strip()}")
        print(f"Путь к файлу: {log_file_path}")
        
    except Exception as e:
        print(f"Ошибка записи в лог: {e}")
        # Запишем в системную папку temp как fallback
        temp_log = os.path.join(os.environ.get('TEMP', '/tmp'), 'data-2.log')
        with open(temp_log, 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry)
        print(f"Записано в резервный лог: {temp_log}")

if __name__ == "__main__":
    write_to_log()