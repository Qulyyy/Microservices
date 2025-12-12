import pytest
import requests
import time

BASE_URL = 'http://localhost:5004'
AUTH_URL = 'http://localhost:5001'

@pytest.fixture(scope='session')
def wait_for_services():
    """Ожидание запуска сервисов"""
    max_attempts = 30
    for i in range(max_attempts):
        try:
            auth_response = requests.get(f'{AUTH_URL}/health', timeout=2)
            submission_response = requests.get(f'{BASE_URL}/health', timeout=2)
            if auth_response.status_code == 200 and submission_response.status_code == 200:
                return
        except:
            pass
        time.sleep(1)
    pytest.fail("Сервисы не запустились")

@pytest.fixture(scope='session')
def auth_token(wait_for_services):
    """Получение токена авторизации"""
    username = f'submission_user_{int(time.time())}'
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
    assert data['service'] == 'submission_service'

def test_create_submission(wait_for_services, auth_token):
    """E2E тест создания сабмишена"""
    response = requests.post(
        f'{BASE_URL}/submissions',
        headers={'Authorization': f'Bearer {auth_token}'},
        json={
            'problem_id': 'problem_1',
            'code': 'print("Hello, World!")',
            'language': 'python'
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert 'submission_id' in data
    assert data['problem_id'] == 'problem_1'
    assert data['language'] == 'python'


