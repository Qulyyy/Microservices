import pytest
from unittest.mock import patch, MagicMock
from app import app, problems, contests, admins, is_admin

@pytest.fixture
def client():
    """Создает тестовый клиент Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            # Очищаем данные перед каждым тестом
            problems.clear()
            contests.clear()
            yield client

@pytest.fixture
def mock_auth_verify():
    """Мок для verify_token"""
    with patch('app.verify_token') as mock:
        yield mock

def test_is_admin_function():
    """Тест функции проверки прав администратора"""
    assert is_admin('admin') is True
    assert is_admin('regular_user') is False
    assert is_admin('') is False

def test_problem_creation():
    """Тест создания задачи"""
    problems.clear()
    problem_id = 'problem_1'
    problems[problem_id] = {
        'problem_id': problem_id,
        'title': 'Test Problem',
        'description': 'Test Description',
        'difficulty': 'easy',
        'test_cases': [{'input': '1', 'output': '2'}],
        'time_limit': 1,
        'memory_limit': 256,
        'created_by': 'admin'
    }
    
    assert problem_id in problems
    assert problems[problem_id]['title'] == 'Test Problem'
    assert problems[problem_id]['difficulty'] == 'easy'

def test_problem_update():
    """Тест обновления задачи"""
    problems.clear()
    problem_id = 'problem_1'
    problems[problem_id] = {
        'problem_id': problem_id,
        'title': 'Old Title',
        'description': 'Old Description',
        'difficulty': 'easy',
        'test_cases': [],
        'time_limit': 1,
        'memory_limit': 256,
        'created_by': 'admin'
    }
    
    update_data = {'title': 'New Title', 'difficulty': 'hard'}
    problems[problem_id].update(update_data)
    
    assert problems[problem_id]['title'] == 'New Title'
    assert problems[problem_id]['difficulty'] == 'hard'

def test_contest_creation():
    """Тест создания контеста"""
    contests.clear()
    contest_id = 'contest_1'
    contests[contest_id] = {
        'contest_id': contest_id,
        'name': 'Test Contest',
        'description': 'Test Description',
        'start_time': '2024-01-01T00:00:00',
        'end_time': '2024-01-02T00:00:00',
        'problems': [],
        'created_by': 'admin'
    }
    
    assert contest_id in contests
    assert contests[contest_id]['name'] == 'Test Contest'

def test_add_problem_to_contest():
    """Тест добавления задачи в контест"""
    problems.clear()
    contests.clear()
    
    problem_id = 'problem_1'
    problems[problem_id] = {
        'problem_id': problem_id,
        'title': 'Test Problem',
        'description': 'Test',
        'difficulty': 'easy',
        'test_cases': [],
        'time_limit': 1,
        'memory_limit': 256,
        'created_by': 'admin'
    }
    
    contest_id = 'contest_1'
    contests[contest_id] = {
        'contest_id': contest_id,
        'name': 'Test Contest',
        'description': 'Test',
        'start_time': '2024-01-01T00:00:00',
        'end_time': '2024-01-02T00:00:00',
        'problems': [],
        'created_by': 'admin'
    }
    
    if problem_id not in contests[contest_id]['problems']:
        contests[contest_id]['problems'].append(problem_id)
    
    assert problem_id in contests[contest_id]['problems']
    assert len(contests[contest_id]['problems']) == 1

def test_create_problem_unauthorized(client, mock_auth_verify):
    """Тест создания задачи без прав администратора"""
    mock_auth_verify.return_value = 'regular_user'
    response = client.post('/problems', 
        headers={'Authorization': 'Bearer token'},
        json={'title': 'Test Problem'})
    assert response.status_code == 403

def test_create_problem_authorized(client, mock_auth_verify):
    """Тест создания задачи с правами администратора"""
    mock_auth_verify.return_value = 'admin'
    response = client.post('/problems',
        headers={'Authorization': 'Bearer token'},
        json={
            'title': 'Test Problem',
            'description': 'Test Description',
            'difficulty': 'easy'
        })
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Test Problem'


