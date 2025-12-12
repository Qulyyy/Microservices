import pytest
import requests
import time

BASE_URL = 'http://localhost:5001'

@pytest.fixture(scope='session')
def wait_for_service():
    """Ожидание запуска сервиса"""
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get(f'{BASE_URL}/health', timeout=2)
            if response.status_code == 200:
                return
        except:
            pass
        time.sleep(1)
    pytest.fail("Сервис не запустился")

def test_health_endpoint(wait_for_service):
    """E2E тест проверки здоровья сервиса"""
    response = requests.get(f'{BASE_URL}/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert data['service'] == 'auth_service'

def test_register_endpoint(wait_for_service):
    """E2E тест регистрации через API"""
    user_data = {
        'username': f'testuser_{int(time.time())}',
        'password': 'password123',
        'email': f'test_{int(time.time())}@example.com'
    }
    
    response = requests.post(f'{BASE_URL}/register', json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert 'успешно зарегистрирован' in data['message']

def test_register_and_login_flow(wait_for_service):
    """E2E тест полного потока регистрации и входа"""
    username = f'user_{int(time.time())}'
    user_data = {
        'username': username,
        'password': 'password123',
        'email': f'{username}@example.com'
    }
    
    # Регистрация
    register_response = requests.post(f'{BASE_URL}/register', json=user_data)
    assert register_response.status_code == 201
    
    # Вход
    login_response = requests.post(f'{BASE_URL}/login', json={
        'username': username,
        'password': 'password123'
    })
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert 'token' in login_data
    assert login_data['user_id'] == username
    
    # Проверка токена
    token = login_data['token']
    verify_response = requests.post(
        f'{BASE_URL}/verify',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert verify_response.status_code == 200
    verify_data = verify_response.json()
    assert verify_data['valid'] is True
    assert verify_data['user_id'] == username

def test_login_with_invalid_credentials(wait_for_service):
    """E2E тест входа с неверными учетными данными"""
    response = requests.post(f'{BASE_URL}/login', json={
        'username': 'nonexistent_user',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401

def test_register_duplicate_user(wait_for_service):
    """E2E тест регистрации дублирующегося пользователя"""
    username = f'duplicate_{int(time.time())}'
    user_data = {
        'username': username,
        'password': 'password123',
        'email': f'{username}@example.com'
    }
    
    # Первая регистрация
    response1 = requests.post(f'{BASE_URL}/register', json=user_data)
    assert response1.status_code == 201
    
    # Попытка повторной регистрации
    response2 = requests.post(f'{BASE_URL}/register', json=user_data)
    assert response2.status_code == 400


