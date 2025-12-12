import pytest
import requests
import time

BASE_URL = 'http://localhost:5002'
AUTH_URL = 'http://localhost:5001'

@pytest.fixture(scope='session')
def wait_for_services():
    """Ожидание запуска сервисов"""
    max_attempts = 30
    for i in range(max_attempts):
        try:
            auth_response = requests.get(f'{AUTH_URL}/health', timeout=2)
            user_response = requests.get(f'{BASE_URL}/health', timeout=2)
            if auth_response.status_code == 200 and user_response.status_code == 200:
                return
        except:
            pass
        time.sleep(1)
    pytest.fail("Сервисы не запустились")

@pytest.fixture(scope='session')
def auth_token(wait_for_services):
    """Получение токена авторизации"""
    username = f'testuser_{int(time.time())}'
    user_data = {
        'username': username,
        'password': 'password123',
        'email': f'{username}@example.com'
    }
    
    # Регистрация
    requests.post(f'{AUTH_URL}/register', json=user_data)
    
    # Вход
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
    assert data['service'] == 'user_service'

def test_get_profile_unauthorized(wait_for_services):
    """E2E тест получения профиля без авторизации"""
    response = requests.get(f'{BASE_URL}/profile/testuser')
    assert response.status_code == 401

def test_get_profile_authorized(wait_for_services, auth_token):
    """E2E тест получения профиля с авторизацией"""
    response = requests.get(
        f'{BASE_URL}/profile/testuser',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'user_id' in data
    assert 'rating' in data

def test_update_profile(wait_for_services, auth_token):
    """E2E тест обновления профиля"""
    username = f'updateuser_{int(time.time())}'
    
    # Создаем пользователя
    requests.post(f'{AUTH_URL}/register', json={
        'username': username,
        'password': 'password123',
        'email': f'{username}@example.com'
    })
    login_resp = requests.post(f'{AUTH_URL}/login', json={
        'username': username,
        'password': 'password123'
    })
    token = login_resp.json()['token']
    
    # Обновляем профиль
    response = requests.put(
        f'{BASE_URL}/profile/{username}',
        headers={'Authorization': f'Bearer {token}'},
        json={'rating': 150, 'solved_problems': 10}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['rating'] == 150
    assert data['solved_problems'] == 10

def test_get_leaderboard(wait_for_services, auth_token):
    """E2E тест получения табло лидеров"""
    response = requests.get(
        f'{BASE_URL}/leaderboard',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'leaderboard' in data

def test_create_team(wait_for_services, auth_token):
    """E2E тест создания команды"""
    response = requests.post(
        f'{BASE_URL}/teams',
        headers={'Authorization': f'Bearer {auth_token}'},
        json={'name': f'Test Team {int(time.time())}'}
    )
    assert response.status_code == 201
    data = response.json()
    assert 'team_id' in data
    assert 'name' in data
    assert 'members' in data


