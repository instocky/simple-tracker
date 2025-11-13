#!/usr/bin/env python3
"""
Простой тест веб-API для Simple Time Tracker (без внешних зависимостей)
"""
import urllib.request
import urllib.parse
import urllib.error
import json
import sys

BASE_URL = "http://127.0.0.1:8080"

def make_request(url, method="GET", data=None):
    """Выполняет HTTP запрос"""
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={
                'Content-Type': 'application/json'
            }, method=method)
        else:
            req = urllib.request.Request(url, method=method)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            try:
                return response.status, json.loads(content)
            except json.JSONDecodeError:
                return response.status, content
                
    except urllib.error.URLError as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)

def test_api():
    """Тестирует основные эндпоинты API"""
    
    print("🚀 Тестирование Simple Time Tracker API")
    print("=" * 50)
    
    # Тест 1: Главная страница
    print("1. Тест главной страницы:")
    status, data = make_request(BASE_URL)
    if status == 200:
        print(f"   ✅ Статус: {status}")
        if isinstance(data, dict):
            print(f"   ✅ Сообщение: {data.get('message', 'N/A')}")
        else:
            print(f"   ✅ Ответ: {data[:100]}...")
    else:
        print(f"   ❌ Ошибка: {status} - {data}")
    print()
    
    # Тест 2: Список проектов
    print("2. Тест списка проектов:")
    status, data = make_request(f"{BASE_URL}/api/projects")
    if status == 200 and isinstance(data, dict):
        projects_data = data.get('data', {})
        projects = projects_data.get('projects', [])
        print(f"   ✅ Статус: {status}")
        print(f"   ✅ Найдено проектов: {len(projects)}")
        if projects:
            first_project = projects[0]
            print(f"   ✅ Первый проект: {first_project.get('title', 'N/A')} ({first_project.get('status', 'N/A')})")
            # Показываем первые 3 проекта
            for i, proj in enumerate(projects[:3], 1):
                status_icon = "🟢" if proj.get('status') == 'active' else "🔵"
                print(f"      {i}. {status_icon} {proj.get('title', 'N/A')} - {proj.get('status', 'N/A')}")
    else:
        print(f"   ❌ Ошибка: {status} - {data}")
    print()
    
    # Тест 3: Активный проект
    print("3. Тест активного проекта:")
    status, data = make_request(f"{BASE_URL}/api/active")
    if status == 200 and isinstance(data, dict):
        project_data = data.get('data', {})
        project = project_data.get('project')
        print(f"   ✅ Статус: {status}")
        if project:
            print(f"   ✅ Активный проект: {project.get('title', 'N/A')} ({project.get('status', 'N/A')})")
        else:
            print("   ℹ️ Нет активного проекта")
    else:
        print(f"   ❌ Ошибка: {status} - {data}")
    print()
    
    # Тест 4: Health check
    print("4. Тест состояния API:")
    status, data = make_request(f"{BASE_URL}/api/health")
    if status == 200 and isinstance(data, dict):
        health_data = data.get('data', {})
        print(f"   ✅ Статус: {status}")
        print(f"   ✅ Состояние: {health_data.get('status', 'N/A')}")
        print(f"   ✅ Проектов в БД: {health_data.get('projects_count', 'N/A')}")
    else:
        print(f"   ❌ Ошибка: {status} - {data}")
    print()
    
    # Тест 5: Активация проекта (тест POST)
    print("5. Тест активации проекта:")
    test_project_name = "kamkb"  # Проект из реальных данных
    status, data = make_request(f"{BASE_URL}/api/start", "POST", {"identifier": test_project_name})
    if status == 200:
        print(f"   ✅ Статус: {status}")
        if isinstance(data, dict):
            print(f"   ✅ Сообщение: {data.get('message', 'N/A')}")
        else:
            print(f"   ✅ Ответ: {data}")
    else:
        print(f"   ❌ Ошибка: {status} - {data}")
    print()
    
    # Тест 6: Проверка активного проекта после активации
    print("6. Проверка активного проекта после активации:")
    status, data = make_request(f"{BASE_URL}/api/active")
    if status == 200 and isinstance(data, dict):
        project_data = data.get('data', {})
        project = project_data.get('project')
        print(f"   ✅ Статус: {status}")
        if project:
            status_icon = "🟢" if project.get('status') == 'active' else "🔵"
            print(f"   ✅ Новый активный проект: {status_icon} {project.get('title', 'N/A')} ({project.get('status', 'N/A')})")
        else:
            print("   ℹ️ Нет активного проекта")
    else:
        print(f"   ❌ Ошибка: {status} - {data}")
    print()
    
    print("🎉 Тестирование завершено!")

if __name__ == "__main__":
    test_api()