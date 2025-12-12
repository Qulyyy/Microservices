import pytest
import requests
import time

BASE_URL = 'http://localhost:5003'
AUTH_URL = 'http://localhost:5001'

@pytest.fixture(scope='session')
def wait_for_services():
    """Ожидание запуска сервисов"""
    max_attempts = 30
    for i in range(max_attempts):
        try:
            auth_response = requests.get(f'{AUTH_URL}/health', timeout=2)
            admin_response = requests.get(f'{BASE_URL}/health', timeout=2)
            if auth_response.status_code == 200 and admin_response.status_code == 200:
                return
        except:
            pass
        time.sleep(1)
    pytest.fail("Сервисы не запустились")

@pytest.fixture(scope='session')
def admin_token(wait_for_services):
    """Получение токена администратора"""
    # Регистрация админа
    username = 'admin'
    user_data = {
        'username': username,
        'password': 'admin123',
        'email': 'admin@example.com'
    }
    
    try:
        requests.post(f'{AUTH_URL}/register', json=user_data)
    except:
        pass  # Может уже существовать
    
    # Вход
    login_response = requests.post(f'{AUTH_URL}/login', json={
        'username': username,
        'password': 'admin123'
    })
    if login_response.status_code == 200:
        return login_response.json()['token']
    return None

@pytest.fixture(scope='session')
def user_token(wait_for_services):
    """Получение токена обычного пользователя"""
    username = f'regular_user_{int(time.time())}'
    user_data = {
        'username': username,
        'password': 'password123',
        'email': f'{username}@example.com'
    }
    
    requests.post(f'{AUTH_URL}/register', json=user_data)
    login_response = requests.post(f'{AUTH_URL}/login', json={
        'username': username,
        'password': 'password123'
    })
    return login_response.json()['token']

def test_health_endpoint(wait_for_services):
    """E2E тест проверки здоровья сервиса"""
    response = requests.get(f'{BASE_URL}/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert data['service'] == 'admin_service'

def test_get_problems_unauthorized(wait_for_services):
    """E2E тест получения задач без авторизации"""
    response = requests.get(f'{BASE_URL}/problems')
    assert response.status_code == 401

def test_get_problems_authorized(wait_for_services, user_token):
    """E2E тест получения задач с авторизацией"""
    response = requests.get(
        f'{BASE_URL}/problems',
        headers={'Authorization': f'Bearer {user_token}'}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'problems' in data

def test_create_problem_as_admin(wait_for_services, admin_token):
    """E2E тест создания задачи администратором"""
    if not admin_token:
        pytest.skip("Админ токен не получен")
    
    problem_data = {
        'title': f'Test Problem {int(time.time())}',
        'description': 'Test Description',
        'difficulty': 'easy',
        'test_cases': [
            {'input': '1 2', 'output': '3'}
        ]
    }
    
    response = requests.post(
        f'{BASE_URL}/problems',
        headers={'Authorization': f'Bearer {admin_token}'},
        json=problem_data
    )
    assert response.status_code == 201
    data = response.json()
    assert data['title'] == problem_data['title']
    assert 'problem_id' in data

def test_create_problem_as_user(wait_for_services, user_token):
    """E2E тест создания задачи обычным пользователем (должно быть запрещено)"""
    problem_data = {
        'title': 'Unauthorized Problem',
        'description': 'Test'
    }
    
    response = requests.post(
        f'{BASE_URL}/problems',
        headers={'Authorization': f'Bearer {user_token}'},
        json=problem_data
    )
    assert response.status_code == 403

def test_create_contest(wait_for_services, admin_token):
    """E2E тест создания контеста"""
    if not admin_token:
        pytest.skip("Админ токен не получен")
    
    contest_data = {
        'name': f'Test Contest {int(time.time())}',
        'description': 'Test Contest Description',
        'start_time': '2024-01-01T00:00:00',
        'end_time': '2024-12-31T23:59:59'
    }
    
    response = requests.post(
        f'{BASE_URL}/contests',
        headers={'Authorization': f'Bearer {admin_token}'},
        json=contest_data
    )
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == contest_data['name']
    assert 'contest_id' in data


