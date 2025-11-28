# API Endpoint: /api/timeline/data

## Описание

Новый API endpoint для получения структурированных данных о временной активности в формате JSON, предназначенный для отрисовки графиков на фронтенде.

## Спецификация

### Запрос

- **Метод**: `GET`
- **URL**: `/api/timeline/data`
- **Параметры**:
  - `date` (обязательный) — дата в формате `YYYY-MM-DD`

### Пример запроса

```url
GET http://localhost:8080/api/timeline/data?date=2025-11-27
```

### Ответ (JSON)

```json
{
  "success": true,
  "date": "2025-11-27",
  "total_active_minutes": 345,
  "hourly_data": [
    {
      "hour": "08:00",
      "active_minutes": 15,
      "total_minutes": 60,
      "status": "low"
    },
    {
      "hour": "09:00",
      "active_minutes": 60,
      "total_minutes": 60,
      "status": "high"
    }
    // ... данные за каждый час с 08:00 до 19:00
  ]
}
```

## Описание полей

### Корневые поля

- `success` (boolean) — статус выполнения запроса
- `date` (string) — дата в формате YYYY-MM-DD
- `total_active_minutes` (integer) — сумма активных минут за весь период
- `hourly_data` (array) — массив данных по часам

### Поля элементов hourly_data

- `hour` (string) — временной слот (начало часа), формат "HH:00"
- `active_minutes` (integer) — количество минут активности в этом часе
- `total_minutes` (integer) — длительность слота (всегда 60)
- `status` (string) — статус активности

## Логика работы

### Диапазон времени

Данные формируются для фиксированных слотов с **08:00** до **19:00** (12 часов).

### Подсчет активных минут

- События типа "Проект" и "Активность" засчитываются в `active_minutes`
- События типа "Простой" (Idle) и "Нет данных" игнорируются
- Каждый бит данных = 5 минут

### Определение статуса

- `idle`: 0 минут активности
- `low`: 1–15 минут
- `medium`: 16–45 минут
- `high`: > 45 минут

## Обработка ошибок

### 1. Отсутствует параметр date

```json
{
  "error": true,
  "message": "Требуется параметр \"date\" в формате YYYY-MM-DD"
}
```

**HTTP Status**: 400 Bad Request

### 2. Неверный формат даты

```json
{
  "error": true,
  "message": "Неверный формат даты. Используйте YYYY-MM-DD"
}
```

**HTTP Status**: 400 Bad Request

### 3. Нет данных за дату

Возвращается структура с `active_minutes: 0` для всех часов:

```json
{
  "success": true,
  "date": "2025-11-27",
  "total_active_minutes": 0,
  "hourly_data": [
    {
      "hour": "08:00",
      "active_minutes": 0,
      "total_minutes": 60,
      "status": "idle"
    }
    // ... все слоты с нулевой активностью
  ]
}
```

### 4. Внутренняя ошибка

```json
{
  "error": true,
  "message": "Ошибка получения данных временной шкалы: <описание ошибки>"
}
```

**HTTP Status**: 500 Internal Server Error

## Примеры использования

### JavaScript (fetch)

```javascript
async function getTimelineData(date) {
  const response = await fetch(`/api/timeline/data?date=${date}`);
  const data = await response.json();

  if (data.success) {
    console.log(`Всего активных минут: ${data.total_active_minutes}`);
    data.hourly_data.forEach(hour => {
      console.log(`${hour.hour}: ${hour.active_minutes} мин (${hour.status})`);
    });
  }
}

// Использование
getTimelineData('2025-11-27');
```

### JavaScript (axios)

```javascript
import axios from 'axios';

async function getTimelineData(date) {
  try {
    const response = await axios.get('/api/timeline/data', {
      params: { date: date },
    });

    return response.data;
  } catch (error) {
    console.error('Ошибка:', error.response.data.message);
  }
}
```

### Python (requests)

```python
import requests

def get_timeline_data(date):
    response = requests.get('http://localhost:8080/api/timeline/data',
                           params={'date': date})

    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"Всего активных минут: {data['total_active_minutes']}")
            for hour in data['hourly_data']:
                print(f"{hour['hour']}: {hour['active_minutes']} мин ({hour['status']})")
    else:
        print(f"Ошибка: {response.json()['message']}")

# Использование
get_timeline_data('2025-11-27')
```

## Интеграция с фронтендом

### Пример для Chart.js

```javascript
function prepareChartData(timelineData) {
  return {
    labels: timelineData.hourly_data.map(h => h.hour),
    datasets: [
      {
        label: 'Активные минуты',
        data: timelineData.hourly_data.map(h => h.active_minutes),
        backgroundColor: timelineData.hourly_data.map(h => {
          switch (h.status) {
            case 'high':
              return '#4CAF50';
            case 'medium':
              return '#FF9800';
            case 'low':
              return '#FFC107';
            case 'idle':
              return '#F44336';
            default:
              return '#9E9E9E';
          }
        }),
      },
    ],
  };
}
```

### Пример для простого отображения

```javascript
function renderTimeline(container, timelineData) {
  container.innerHTML = '';

  timelineData.hourly_data.forEach(hour => {
    const div = document.createElement('div');
    div.className = `timeline-hour status-${hour.status}`;
    div.innerHTML = `
      <span class="time">${hour.hour}</span>
      <span class="minutes">${hour.active_minutes} мин</span>
      <span class="status">${hour.status}</span>
    `;
    container.appendChild(div);
  });
}
```

## Преимущества нового endpoint

1. **Структурированные данные** — готовая для использования JSON структура
2. **Отсутствие парсинга** — не нужно парсить текстовый вывод
3. **Оптимизация для фронтенда** — данные в формате, удобном для графиков
4. **Валидация входных данных** — проверка формата даты и обязательных параметров
5. **Предсказуемая структура** — всегда возвращает 12 часовых слотов с 08:00 до 19:00
6. **Готовые статусы** — вычисленные уровни активности для стилизации

## Связанные endpoints

- `GET /api/timeline` — текстовый отчет временной шкалы (устаревший формат)
- `GET /api/analytics` — общая статистика пассивного отслеживания
- `GET /api/projects` — список проектов и их статусы

## Техническая документация

- **Файл реализации**: `web_server.py`
- **Функции**: `get_timeline_data()`, `calculate_hourly_timeline_data()`, `get_passive_tracking_data_for_date()`
- **Валидация**: Проверка формата даты через `datetime.strptime(date, '%Y-%m-%d')`
- **Источник данных**: БД `db.json` → `meta.passive_tracking.daily_masks[date]`
- **Формат битов**: Каждый бит = 5 минут, с 08:00 до 20:00 (144 слота)
