import pytest
import requests
import time

BASE_URL = 'http://localhost:5005'

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
    assert data['service'] == 'compiler_service'

def test_compile_simple_code(wait_for_service):
    """E2E тест компиляции простого кода"""
    response = requests.post(
        f'{BASE_URL}/compile',
        json={
            'submission_id': 'test_1',
            'code': 'print("Hello")',
            'language': 'python',
            'problem_id': None
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert 'status' in data

def test_compile_code_with_test_cases(wait_for_service):
    """E2E тест компиляции кода с тест-кейсами"""
    response = requests.post(
        f'{BASE_URL}/compile',
        json={
            'submission_id': 'test_2',
            'code': 'a, b = map(int, input().split())\nprint(a + b)',
            'language': 'python',
            'problem_id': None
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert 'status' in data


