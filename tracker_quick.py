#!/usr/bin/env python3
"""
Быстрый трекер времени для планировщика
"""
import datetime
import json
import os
import sys

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
        
        # Находим активный проект
        current_project = None
        for project in data['projects']:
            if project.get('status') == 'active':
                current_project = project
                break
        
        if not current_project:
            return False
        
        # Вычисляем позицию бита (каждые 5 минут с 08:00)
        start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
        time_diff = now - start_time
        total_minutes = int(time_diff.total_seconds() / 60)
        bit_position = total_minutes // 5
        
        if bit_position < 0 or bit_position >= 144:
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
            
            # Пересчитываем общее время
            total_minutes = 0
            for mask in current_project['daily_masks'].values():
                total_minutes += mask.count('1') * 5
            current_project['total_minutes'] = total_minutes
            
            # Сохраняем
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Пишем в лог
            log_entry = f"{now.strftime('%Y-%m-%d %H:%M')} | {current_project['title']} | BIT_SET | Position: {bit_position}\n"
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        
        return True
        
    except Exception:
        return False

if __name__ == "__main__":
    success = quick_track()
    sys.exit(0 if success else 1)
