#!/usr/bin/env python3
"""
Простой тест веб-API для Simple Time Tracker
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_api():
    """Тестирует основные эндпоинты API"""
    
    print("🚀 Тестирование Simple Time Tracker API")
    print("=" * 50)
    
    try:
        # Тест 1: Главная страница
        print("1. Тест главной страницы:")
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Статус: {response.status_code}")
            print(f"   ✅ Сообщение: {data.get('message', 'N/A')}")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
        print()
        
        # Тест 2: Список проектов
        print("2. Тест списка проектов:")
        response = requests.get(f"{BASE_URL}/api/projects")
        if response.status_code == 200:
            data = response.json()
            projects = data.get('data', {}).get('projects', [])
            print(f"   ✅ Статус: {response.status_code}")
            print(f"   ✅ Найдено проектов: {len(projects)}")
            if projects:
                print(f"   ✅ Первый проект: {projects[0].get('title', 'N/A')} ({projects[0].get('status', 'N/A')})")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
        print()
        
        # Тест 3: Активный проект
        print("3. Тест активного проекта:")
        response = requests.get(f"{BASE_URL}/api/active")
        if response.status_code == 200:
            data = response.json()
            project = data.get('data', {}).get('project')
            print(f"   ✅ Статус: {response.status_code}")
            if project:
                print(f"   ✅ Активный проект: {project.get('title', 'N/A')} ({project.get('status', 'N/A')})")
            else:
                print("   ℹ️ Нет активного проекта")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
        print()
        
        # Тест 4: Health check
        print("4. Тест состояния API:")
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            health_data = data.get('data', {})
            print(f"   ✅ Статус: {response.status_code}")
            print(f"   ✅ Состояние: {health_data.get('status', 'N/A')}")
            print(f"   ✅ Проектов в БД: {health_data.get('projects_count', 'N/A')}")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
        print()
        
        # Тест 5: Активация проекта (тест POST)
        print("5. Тест активации проекта:")
        test_project_name = "kamkb"  # Проект из реальных данных
        response = requests.post(f"{BASE_URL}/api/start", 
                                json={"identifier": test_project_name})
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Статус: {response.status_code}")
            print(f"   ✅ Сообщение: {data.get('message', 'N/A')}")
        else:
            print(f"   ❌ Ошибка: {response.status_code} - {response.text}")
        print()
        
        # Тест 6: Проверка активного проекта после активации
        print("6. Проверка активного проекта после активации:")
        response = requests.get(f"{BASE_URL}/api/active")
        if response.status_code == 200:
            data = response.json()
            project = data.get('data', {}).get('project')
            print(f"   ✅ Статус: {response.status_code}")
            if project:
                print(f"   ✅ Новый активный проект: {project.get('title', 'N/A')} ({project.get('status', 'N/A')})")
            else:
                print("   ℹ️ Нет активного проекта")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
        print()
        
        print("🎉 Тестирование завершено!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: Не удается подключиться к серверу")
        print("   Убедитесь, что веб-сервер запущен на http://127.0.0.1:8080")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    test_api()