# Simple Time Tracker

Автоматический трекер времени работы над проектами с поддержкой **неограниченной иерархии** и JSON-базой данных.

## 🚀 Основные возможности

- ✅ **Иерархические проекты** с неограниченной вложенностью
- ✅ **Автоматический трекинг** времени каждые 5 минут
- ✅ **Агрегированное время** с учетом всех дочерних проектов
- ✅ **CLI интерфейс** с расширенными командами
- ✅ **Обратная совместимость** со старыми данными
- ✅ **Автоматическая миграция** данных с backup
- ✅ **Производительность** <500ms для трекера

## 📁 Архитектура проекта

```
simple-tracker/
├── core/                    # 🔧 Модули иерархии
│   ├── transliteration.py   # Транслитерация RU→EN
│   ├── compatibility.py     # Поддержка старого формата
│   ├── hierarchy.py         # Алгоритмы иерархии
│   └── console_utils.py     # Unicode-безопасный вывод
├── tests/                   # 🧪 Тестовая инфраструктура
│   ├── test_core.py         # Тесты core модулей
│   ├── manual_tracker_test.py # Тесты трекера
│   ├── demo_hierarchy_tracker.py # Демо иерархии
│   └── run_all.py           # Запуск всех тестов
├── legacy/                  # 📦 Backup оригиналов
│   ├── tracker_quick_original.py
│   └── project_manager_original.py
├── tracker_quick.py         # ⚡ Трекер с иерархией
├── project_manager.py       # 🎛️ CLI с новыми командами
├── db.json                  # 🗄️ БД в новом формате
├── run_silent.vbs          # ⏰ Windows планировщик
└── specification_0607.md   # 📋 Техзадание
```

## 🎯 Использование

### Настройка планировщика
1. Создать задачу в планировщике Windows
2. Запускать `run_silent.vbs` каждые 5 минут  
3. Трекер автоматически отмечает время активного проекта

### Основные команды
```bash
# Показать все проекты (адаптивный вывод)
python project_manager.py list

# Древовидная структура проектов
python project_manager.py tree

# Информация о базе данных
python project_manager.py info

# Справка по командам
python project_manager.py help
```

### Управление проектами
```bash
# Создать корневой проект
python project_manager.py create "Новый проект"

# Создать дочерний проект
python project_manager.py create "Frontend" --parent "exlibrus"
python project_manager.py create "Components" --parent "exlibrus/frontend"

# Универсальный поиск и активация
python project_manager.py active "exlibrus"              # по названию
python project_manager.py active "exlibrus-frontend"     # по ID
python project_manager.py active "exlibrus/frontend"     # по path

# Установить статус проекта
python project_manager.py status "Frontend" completed
```

### Миграция данных
```bash
# Информация о текущем формате
python project_manager.py info

# Автоматическая миграция в новый формат (с backup)
python project_manager.py migrate
```

## 📊 Структура данных

### Новый формат БД (поддерживает иерархию)
```json
{
  "meta": {
    "work_hours": {"start": "08:00", "end": "20:00"},
    "time_tracking": {"interval_minutes": 5, "total_daily_slots": 144}
  },
  "projects": [
    {
      "id": "exlibrus",
      "path": "exlibrus", 
      "title": "ExLibrus",
      "status": "active",
      "fill_color": "#4CAF50",
      "total_minutes": 335,          // собственное время
      "aggregated_minutes": 520,     // общее время с дочерними
      "daily_masks": {
        "2025-06-07": "110010000100010000000000..."
      }
    },
    {
      "id": "exlibrus-frontend",
      "path": "exlibrus/frontend",
      "title": "Frontend", 
      "status": "paused",
      "total_minutes": 120,
      "aggregated_minutes": 185,     // 120 + 65 (дочерние)
      "daily_masks": {...}
    }
  ]
}
```

### Ключевые поля
- **`id`**: Уникальный идентификатор (транслитерация title)
- **`path`**: Иерархический путь проекта (`parent/child`)  
- **`total_minutes`**: Собственное время проекта
- **`aggregated_minutes`**: Общее время (свое + всех дочерних)

## 🎛️ CLI команды

### Просмотр проектов
```bash
list                # Адаптивный список (старый/новый формат)
tree                # Древовидная структура с иерархией
info                # Информация о БД и статистика
```

### Управление проектами  
```bash
active <идентификатор>         # Сделать проект активным
status <идентификатор> <статус> # Установить статус
create <название>              # Создать корневой проект
create <название> --parent <path> # Создать дочерний проект
```

### Системные команды
```bash
migrate             # Миграция в новый формат
help                # Справка по командам
```

### Статусы проектов
- `active` - текущий проект (идет трекинг времени)
- `paused` - приостановлен  
- `completed` - завершен успешно
- `archived` - архивирован

## ⚡ Принцип работы

### Трекинг времени
1. **Битовые маски**: каждый 5-минутный интервал = 1 бит (08:00-20:00 = 144 бита)
2. **Автоматический трекинг**: планировщик запускает `tracker_quick.py` каждые 5 минут
3. **Иерархическое обновление**: время автоматически агрегируется вверх по дереву
4. **Производительность**: трекер работает <500ms без зависания

### Агрегированное время
```
ExLibrus (50 мин)                    → aggregated: 230 мин
├── Frontend (120 мин)               → aggregated: 180 мин  
│   └── Components (60 мин)          → aggregated: 60 мин
└── Backend (100 мин)                → aggregated: 100 мин
```

**Расчет**: ExLibrus = 50 (свои) + 180 (Frontend) + 100 (Backend) = 330 мин

## 🧪 Тестирование

```bash
# Запуск всех тестов
python tests/run_all.py

# Тестирование core модулей
python tests/test_core.py

# Тестирование трекера  
python tests/manual_tracker_test.py

# Демонстрация иерархии
python tests/demo_hierarchy_tracker.py
```

## 🔄 Совместимость

### Обратная совместимость
- ✅ **Старые данные** автоматически поддерживаются
- ✅ **Существующие команды** работают как раньше
- ✅ **Планировщик** не требует изменений
- ✅ **Graceful fallback** при отсутствии core модулей

### Миграция
1. **Автоматическое определение** формата БД
2. **Безопасная миграция** с созданием backup
3. **Генерация полей** id, path, aggregated_minutes
4. **Валидация целостности** иерархии

## 🛠️ Разработка

### Модульная архитектура
- **`core/transliteration.py`**: Конвертация русских названий в path/id
- **`core/compatibility.py`**: Поддержка старого формата (TODO: LEGACY_SUPPORT)
- **`core/hierarchy.py`**: Алгоритмы работы с иерархией проектов
- **`core/console_utils.py`**: Безопасный вывод в Windows консоль

### Маркеры legacy кода
Весь код совместимости помечен `# TODO: LEGACY_SUPPORT` для последующего удаления после полной миграции.

## 📝 Примеры использования

### Создание иерархии проектов
```bash
# Создаем основной проект
python project_manager.py create "ExLibrus"

# Добавляем подпроекты
python project_manager.py create "Frontend" --parent "exlibrus"
python project_manager.py create "Backend" --parent "exlibrus"  
python project_manager.py create "Components" --parent "exlibrus/frontend"

# Активируем глубокий подпроект
python project_manager.py active "exlibrus/frontend/components"

# Просматриваем структуру
python project_manager.py tree
```

### Результат
```
ExLibrus [пауза]
  5ч35м собств. / 6ч40м общее
+- Frontend [пауза]
     2ч20м собств. / 3ч5м общее  
   +- Components [активен]
        0ч45м собств. / 0ч45м общее
+- Backend [пауза]
     1ч10м собств. / 1ч10м общее
```

---

**Simple Time Tracker** - мощный инструмент для автоматического отслеживания времени работы над иерархическими проектами с полной обратной совместимостью и безопасной миграцией данных.
