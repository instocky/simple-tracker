#!/usr/bin/env python3
"""
Веб-сервер для Simple Time Tracker Dashboard
Flask приложение с REST API для управления проектами
"""

import sys
import os
import json
import argparse
from datetime import datetime

# Добавляем текущую директорию в путь для импорта project_manager
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    import project_manager
except ImportError as e:
    print(f"ОШИБКА: Не удалось импортировать зависимости: {e}")
    print("Попытка автоматической установки...")
    
    # Автоматическая установка Flask и Flask-CORS
    try:
        import subprocess
        import sys
        
        # Создаем virtual environment если его нет
        venv_path = os.path.join(os.path.dirname(__file__), 'venv')
        if not os.path.exists(venv_path):
            print("Создание виртуального окружения...")
            import venv
            venv.create(venv_path, with_pip=True)
        
        # Устанавливаем зависимости
        if sys.platform == 'win32':
            python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
            pip_path = os.path.join(venv_path, 'Scripts', 'pip.exe')
        else:
            python_path = os.path.join(venv_path, 'bin', 'python')
            pip_path = os.path.join(venv_path, 'bin', 'pip')
        
        print("Установка Flask и Flask-CORS...")
        subprocess.run([pip_path, 'install', 'flask', 'flask-cors'], check=True)
        
        # Перезапускаем с новым Python
        print("Перезапуск с установленными зависимостями...")
        os.execv(python_path, [python_path] + sys.argv)
        
    except Exception as install_error:
        print(f"ОШИБКА установки зависимостей: {install_error}")
        print()
        print("РУЧНАЯ УСТАНОВКА:")
        print("1. python -m venv venv")
        print("2. venv/Scripts/activate  # Windows")
        print("   source venv/bin/activate  # Linux/Mac")
        print("3. pip install flask flask-cors")
        print("4. python web_server.py")
        sys.exit(1)

# Создаем Flask приложение
app = Flask(__name__)
CORS(app)  # Разрешаем CORS для разработки

# Настройки
app.config['JSON_AS_ASCII'] = False  # Поддержка кириллицы
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


def json_error(message, status_code=400, details=None):
    """Возвращает ошибку в JSON формате"""
    response = {
        'error': True,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    if details:
        response['details'] = details
    
    return jsonify(response), status_code


def json_success(data=None, message=None):
    """Возвращает успешный ответ в JSON формате"""
    response = {
        'success': True,
        'timestamp': datetime.now().isoformat()
    }
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    
    return jsonify(response)


def calculate_today_minutes(project):
    """Вычисляет время проекта за сегодня"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        daily_masks = project.get('daily_masks', {})
        today_mask = daily_masks.get(today, "")
        
        if not today_mask:
            return 0
        
        # Считаем активные биты (каждый бит = 5 минут)
        active_bits = today_mask.count('1')
        return active_bits * 5
    except:
        return 0


def format_project_for_api(project):
    """Форматирует проект для JSON API"""
    total_mins = project.get('total_minutes', 0)
    aggregated_mins = project.get('aggregated_minutes', total_mins)
    today_mins = calculate_today_minutes(project)
    
    # Форматирование времени
    total_h, total_m = divmod(total_mins, 60)
    agg_h, agg_m = divmod(aggregated_mins, 60)
    today_h, today_m = divmod(today_mins, 60)
    
    return {
        'id': project.get('id', ''),
        'path': project.get('path', ''),
        'title': project.get('title', ''),
        'status': project.get('status', 'paused'),
        'total_minutes': total_mins,
        'aggregated_minutes': aggregated_mins,
        'today_minutes': today_mins,
        'total_time': f"{total_h}ч {total_m}м",
        'aggregated_time': f"{agg_h}ч {agg_m}м",
        'today_time': f"{today_h}ч {today_m}м" if today_mins > 0 else "0м",
        'fill_color': project.get('fill_color', '#4CAF50'),
        'description': project.get('description', ''),
        'daily_masks': project.get('daily_masks', {})
    }


def sort_projects_for_api(projects):
    """Сортировка проектов по времени последней активности"""
    def sort_key(project):
        # Активный проект всегда сверху
        if project.get('status') == 'active':
            return (0, 0)  # Активные проекты в начале
        
        # Остальные по aggregated_minutes (убывание)
        aggregated_mins = project.get('aggregated_minutes', 0)
        title = project.get('title', '')
        
        return (1, -aggregated_mins, title.lower())
    
    return sorted(projects, key=sort_key)


def calculate_hourly_timeline_data(date, data):
    """
    Вычисляет почасовые данные для временной шкалы с поддержкой Task Swimlanes
    
    Args:
        date (str): Дата в формате YYYY-MM-DD
        data (dict): Полная БД с проектами и пассивным отслеживанием
    
    Returns:
        dict: Структурированные данные для API с breakdown по проектам
    """
    hourly_data = []
    total_active_minutes = 0
    
    # 1. Получаем глобальные маски активности (для высоты столбцов)
    daily_masks = get_passive_tracking_data_for_date(data, date)
    
    # 2. Получаем список всех проектов (для генерации полосок задач)
    projects = data.get('projects', [])
    
    # Диапазон времени: 08:00-19:00 (12 часов)
    for hour in range(8, 20):
        hour_start = (hour - 8) * 12  # 12 слотов по 5 минут в часе
        hour_end = hour_start + 12
        
        active_minutes = 0
        project_minutes = 0
        tasks = []  # Новый массив для задач (проектов) этого часа
        
        # --- А. Считаем общую статистику (Высота столбцов) ---
        if daily_masks:
            max_len_active = len(daily_masks.get('computer_activity', ''))
            max_len_project = len(daily_masks.get('project_activity', ''))
            
            for slot in range(hour_start, min(hour_end, 144)):
                # Считаем общую активность (Computer)
                if slot < max_len_active:
                    # Активность = либо есть флаг активности, либо флаг проекта
                    if (daily_masks['computer_activity'][slot] == '1' or 
                        (slot < max_len_project and daily_masks['project_activity'][slot] == '1')):
                        active_minutes += 5
                
                # Считаем общее проектное время (Global Project)
                if slot < max_len_project and daily_masks['project_activity'][slot] == '1':
                    project_minutes += 5
        
        # --- Б. Считаем статистику по конкретным проектам (Цветные полоски) ---
        for project in projects:
            # Получаем маску конкретного проекта за эту дату
            p_daily_masks = project.get('daily_masks', {})
            p_mask = p_daily_masks.get(date, '')
            
            if not p_mask:
                continue
                
            p_minutes_in_hour = 0
            p_max_len = len(p_mask)
            
            # Считаем биты этого проекта в текущем часовом окне
            for slot in range(hour_start, min(hour_end, 144)):
                if slot < p_max_len and p_mask[slot] == '1':
                    p_minutes_in_hour += 5
            
            # Если проект был активен в этом часе, добавляем его в список задач
            if p_minutes_in_hour > 0:
                tasks.append({
                    'id': project.get('id', ''),
                    'title': project.get('title', 'Без названия'),
                    'minutes': p_minutes_in_hour,
                    'color': project.get('fill_color', '#4CAF50')
                })
        
        # Сортируем задачи: самый активный проект идет первым
        # (Это важно для фронтенда: цвет полоски берется от первого проекта в списке)
        tasks.sort(key=lambda x: x['minutes'], reverse=True)
        
        # Определяем статус активности (вспомогательное поле)
        if active_minutes == 0:
            status = 'idle'
        elif active_minutes <= 15:
            status = 'low'
        elif active_minutes <= 45:
            status = 'medium'
        else:
            status = 'high'
        
        # Формируем объект данных за час
        hourly_data.append({
            'hour': f"{hour:02d}:00",
            'active_minutes': active_minutes,
            'project_minutes': project_minutes,
            'total_minutes': 60,
            'status': status,
            'tasks': tasks  # <--- Передаем детализацию по проектам
        })
        
        total_active_minutes += active_minutes
    
    return {
        'success': True,
        'date': date,
        'total_active_minutes': total_active_minutes,
        'hourly_data': hourly_data
    }


def get_passive_tracking_data_for_date(data, date):
    """
    Получает данные пассивного отслеживания за указанную дату
    
    Args:
        data (dict): Данные БД
        date (str): Дата в формате YYYY-MM-DD
    
    Returns:
        dict: Данные пассивного отслеживания или None
    """
    if 'passive_tracking' not in data.get('meta', {}):
        return None
    
    passive = data['meta']['passive_tracking']
    
    if not passive.get('enabled', True):
        return None
    
    if date not in passive.get('daily_masks', {}):
        return None
    
    return passive['daily_masks'][date]


# ==================== API ЭНДПОИНТЫ ====================

@app.route('/')
def index():
    """Главная страница - перенаправление на дашборд"""
    import os
    web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
    index_path = os.path.join(web_dir, 'index.html')
    
    if os.path.exists(index_path):
        # Serve the HTML dashboard
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    else:
        # Fallback to API info if dashboard not found
        return json_success({
            'message': 'Simple Time Tracker API',
            'version': '1.0.0',
            'dashboard': 'HTML dashboard not found',
            'endpoints': [
                'GET  /api/projects',
                'GET  /api/active', 
                'POST /api/start',
                'POST /api/pause',
                'POST /api/complete',
                'POST /api/archive',
                'GET  /api/analytics',
                'GET  /api/timeline',
                'GET  /api/timeline/data'
            ]
        }, message='Добро пожаловать в Simple Time Tracker API!')


@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files"""
    import os
    web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
    css_path = os.path.join(web_dir, 'css', filename)
    
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/css'}
    else:
        return "CSS file not found", 404


@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files"""
    import os
    web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
    js_path = os.path.join(web_dir, 'js', filename)
    
    if os.path.exists(js_path):
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'application/javascript'}
    else:
        return "JavaScript file not found", 404


@app.route('/lib/<path:filename>')
def serve_lib(filename):
    """Serve library files"""
    import os
    web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
    lib_path = os.path.join(web_dir, 'lib', filename)
    
    if os.path.exists(lib_path):
        with open(lib_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Determine content type based on file extension
        if filename.endswith('.js'):
            content_type = 'application/javascript'
        elif filename.endswith('.css'):
            content_type = 'text/css'
        else:
            content_type = 'application/octet-stream'
        return content, 200, {'Content-Type': content_type}
    else:
        return "Library file not found", 404


@app.route('/api/projects', methods=['GET'])
def get_projects():
    """GET /api/projects - список всех проектов с сортировкой"""
    try:
        # Загружаем БД
        data, _ = project_manager.load_db()
        projects = data.get('projects', [])
        
        # Форматируем и сортируем
        formatted_projects = [format_project_for_api(p) for p in projects]
        sorted_projects = sort_projects_for_api(formatted_projects)
        
        return json_success({
            'projects': sorted_projects,
            'total': len(sorted_projects)
        })
        
    except Exception as e:
        return json_error(f"Ошибка загрузки проектов: {str(e)}", 500)


@app.route('/api/active', methods=['GET'])
def get_active_project():
    """GET /api/active - получить активный проект"""
    try:
        data, _ = project_manager.load_db()
        projects = data.get('projects', [])
        
        # Ищем активный проект
        active_project = None
        for project in projects:
            if project.get('status') == 'active':
                active_project = project
                break
        
        if active_project:
            return json_success({
                'project': format_project_for_api(active_project)
            })
        else:
            return json_success({
                'project': None,
                'message': 'Нет активного проекта'
            })
            
    except Exception as e:
        return json_error(f"Ошибка получения активного проекта: {str(e)}", 500)


@app.route('/api/start', methods=['POST'])
def start_project():
    """POST /api/start - активировать проект"""
    try:
        data = request.get_json()
        if not data or 'identifier' not in data:
            return json_error('Требуется параметр "identifier"', 400)
        
        identifier = data['identifier']
        
        # Используем существующую функцию project_manager
        if project_manager.set_active_project(identifier):
            # Получаем обновленный активный проект
            active_data, _ = project_manager.load_db()
            active_project = None
            for project in active_data['projects']:
                if project.get('status') == 'active':
                    active_project = project
                    break
            
            return json_success({
                'project': format_project_for_api(active_project) if active_project else None
            }, message=f'Проект "{identifier}" активирован')
        else:
            return json_error(f'Проект "{identifier}" не найден', 404)
            
    except Exception as e:
        return json_error(f"Ошибка активации проекта: {str(e)}", 500)


@app.route('/api/pause', methods=['POST'])
def pause_project():
    """POST /api/pause - приостановить проект"""
    try:
        data = request.get_json()
        if not data or 'identifier' not in data:
            return json_error('Требуется параметр "identifier"', 400)
        
        identifier = data['identifier']
        
        if project_manager.set_project_status(identifier, 'paused'):
            return json_success(message=f'Проект "{identifier}" приостановлен')
        else:
            return json_error(f'Проект "{identifier}" не найден', 404)
            
    except Exception as e:
        return json_error(f"Ошибка приостановки проекта: {str(e)}", 500)


@app.route('/api/complete', methods=['POST'])
def complete_project():
    """POST /api/complete - завершить проект"""
    try:
        data = request.get_json()
        if not data or 'identifier' not in data:
            return json_error('Требуется параметр "identifier"', 400)
        
        identifier = data['identifier']
        
        if project_manager.set_project_status(identifier, 'completed'):
            return json_success(message=f'Проект "{identifier}" завершен')
        else:
            return json_error(f'Проект "{identifier}" не найден', 404)
            
    except Exception as e:
        return json_error(f"Ошибка завершения проекта: {str(e)}", 500)


@app.route('/api/archive', methods=['POST'])
def archive_project():
    """POST /api/archive - архивировать проект"""
    try:
        data = request.get_json()
        if not data or 'identifier' not in data:
            return json_error('Требуется параметр "identifier"', 400)
        
        identifier = data['identifier']
        
        if project_manager.set_project_status(identifier, 'archived'):
            return json_success(message=f'Проект "{identifier}" архивирован')
        else:
            return json_error(f'Проект "{identifier}" не найден', 404)
            
    except Exception as e:
        return json_error(f"Ошибка архивирования проекта: {str(e)}", 500)


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """GET /api/analytics - статистика пассивного отслеживания"""
    try:
        # Получаем дату из параметров (опционально)
        date = request.args.get('date')
        
        # Захватываем stdout для получения результата show_passive_stats
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            success = project_manager.show_passive_stats(date)
        
        output = f.getvalue()
        
        if not success:
            return json_success({
                'stats': None,
                'message': 'Нет данных пассивного отслеживания' if not date else f'Нет данных за {date}',
                'available_dates': None
            })
        
        # Парсим вывод для извлечения данных
        stats_data = {
            'raw_output': output,
            'date': date or 'последняя доступная',
            'parsed': False  # Можно улучшить парсинг позже
        }
        
        return json_success({
            'analytics': stats_data
        })
        
    except Exception as e:
        return json_error(f"Ошибка получения аналитики: {str(e)}", 500)


@app.route('/api/timeline', methods=['GET'])
def get_timeline():
    """GET /api/timeline - временная шкала активности"""
    try:
        # Получаем дату из параметров (опционально)
        date = request.args.get('date')
        
        # Захватываем stdout для получения результата show_passive_timeline
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            success = project_manager.show_passive_timeline(date)
        
        output = f.getvalue()
        
        if not success:
            return json_success({
                'timeline': None,
                'message': 'Нет данных временной шкалы' if not date else f'Нет данных за {date}',
                'available_dates': None
            })
        
        # Парсим вывод для извлечения данных
        timeline_data = {
            'raw_output': output,
            'date': date or 'последняя доступная',
            'parsed': False  # Можно улучшить парсинг позже
        }
        
        return json_success({
            'timeline': timeline_data
        })
        
    except Exception as e:
        return json_error(f"Ошибка получения временной шкалы: {str(e)}", 500)


@app.route('/api/timeline/data', methods=['GET'])
def get_timeline_data():
    """GET /api/timeline/data - структурированные данные временной активности"""
    try:
        # Получаем и валидируем дату
        date = request.args.get('date')
        if not date:
            return json_error('Требуется параметр "date" в формате YYYY-MM-DD', 400)
        
        # Валидируем формат даты
        try:
            from datetime import datetime
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return json_error('Неверный формат даты. Используйте YYYY-MM-DD', 400)
        
        # Загружаем БД
        data, _ = project_manager.load_db()
        
        # Получаем данные пассивного отслеживания
        daily_masks = get_passive_tracking_data_for_date(data, date)
        
        if daily_masks is None:
            # Если данных за дату нет, возвращаем пустую структуру с пустыми проектами
            empty_data = data.copy()
            if 'meta' not in empty_data:
                empty_data['meta'] = {}
            if 'passive_tracking' not in empty_data['meta']:
                empty_data['meta']['passive_tracking'] = {'daily_masks': {}}
            empty_data['meta']['passive_tracking']['daily_masks'][date] = {
                'computer_activity': '',
                'project_activity': '',
                'idle_periods': '',
                'untracked_work': ''
            }
            return json_success(calculate_hourly_timeline_data(date, empty_data))
        
        # Вычисляем структурированные данные с поддержкой Task Swimlanes
        timeline_data = calculate_hourly_timeline_data(date, data)
        
        return jsonify(timeline_data)
        
    except Exception as e:
        return json_error(f"Ошибка получения данных временной шкалы: {str(e)}", 500)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка состояния API"""
    try:
        # Проверяем доступность БД
        data, _ = project_manager.load_db()
        project_count = len(data.get('projects', []))
        
        return json_success({
            'status': 'healthy',
            'database': 'connected',
            'projects_count': project_count,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return json_error(f"Health check failed: {str(e)}", 503)


# Обработчики ошибок
@app.errorhandler(404)
def not_found(error):
    return json_error('API endpoint не найден', 404)


@app.errorhandler(500)
def internal_error(error):
    return json_error('Внутренняя ошибка сервера', 500)


@app.errorhandler(405)
def method_not_allowed(error):
    return json_error('Метод не разрешен для этого endpoint', 405)


def create_app():
    """Создание и настройка Flask приложения"""
    return app


def main():
    """Главная функция запуска сервера"""
    parser = argparse.ArgumentParser(description='Simple Time Tracker Web Dashboard')
    parser.add_argument('--host', default='127.0.0.1', help='Host для привязки (по умолчанию: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8080, help='Порт для привязки (по умолчанию: 8080)')
    parser.add_argument('--debug', action='store_true', help='Включить debug режим')
    parser.add_argument('--daemon', action='store_true', help='Запуск в фоновом режиме')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("🚀 Simple Time Tracker Web Dashboard")
    print("=" * 50)
    print(f"API доступно на: http://{args.host}:{args.port}")
    print(f"Debug режим: {'Включен' if args.debug else 'Отключен'}")
    print(f"Режим запуска: {'Демон' if args.daemon else 'Обычный'}")
    print("=" * 50)
    print()
    
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()