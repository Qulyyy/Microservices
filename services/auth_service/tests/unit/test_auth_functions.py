import pytest
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, users_db

@pytest.fixture
def client():
    """Создает тестовый клиент Flask"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        with app.app_context():
            # Очищаем базу данных перед каждым тестом
            users_db.clear()
            yield client

@pytest.fixture
def sample_user_data():
    """Фикстура с данными тестового пользователя"""
    return {
        'username': 'testuser',
        'password': 'password123',
        'email': 'test@example.com'
    }

def test_password_hashing():
    """Тест хеширования пароля"""
    password = 'testpassword'
    hash1 = generate_password_hash(password)
    hash2 = generate_password_hash(password)
    
    # Хеши должны быть разными (из-за соли)
    assert hash1 != hash2
    
    # Но оба должны проверяться корректно
    assert check_password_hash(hash1, password)
    assert check_password_hash(hash2, password)
    assert not check_password_hash(hash1, 'wrongpassword')

def test_jwt_token_creation():
    """Тест создания JWT токена"""
    secret_key = 'test-secret-key'
    payload = {
        'user_id': 'testuser',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    assert token is not None
    assert isinstance(token, str)
    
    # Декодирование токена
    decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
    assert decoded['user_id'] == 'testuser'

def test_register_user_success(client, sample_user_data):
    """Тест успешной регистрации пользователя"""
    response = client.post('/register', json=sample_user_data)
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Пользователь успешно зарегистрирован'
    assert sample_user_data['username'] in users_db

def test_register_user_missing_fields(client):
    """Тест регистрации с отсутствующими полями"""
    # Без username
    response = client.post('/register', json={
        'password': 'pass',
        'email': 'test@example.com'
    })
    assert response.status_code == 400
    
    # Без password
    response = client.post('/register', json={
        'username': 'user',
        'email': 'test@example.com'
    })
    assert response.status_code == 400
    
    # Без email
    response = client.post('/register', json={
        'username': 'user',
        'password': 'pass'
    })
    assert response.status_code == 400

def test_register_duplicate_user(client, sample_user_data):
    """Тест регистрации дублирующегося пользователя"""
    # Первая регистрация
    client.post('/register', json=sample_user_data)
    
    # Попытка зарегистрировать того же пользователя
    response = client.post('/register', json=sample_user_data)
    assert response.status_code == 400
    data = response.get_json()
    assert 'уже существует' in data['message']

def test_login_success(client, sample_user_data):
    """Тест успешного входа"""
    # Сначала регистрируем пользователя
    client.post('/register', json=sample_user_data)
    
    # Затем логинимся
    response = client.post('/login', json={
        'username': sample_user_data['username'],
        'password': sample_user_data['password']
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert data['user_id'] == sample_user_data['username']
    
    # Проверяем, что токен валидный
    token = data['token']
    decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    assert decoded['user_id'] == sample_user_data['username']

def test_login_wrong_password(client, sample_user_data):
    """Тест входа с неверным паролем"""
    client.post('/register', json=sample_user_data)
    
    response = client.post('/login', json={
        'username': sample_user_data['username'],
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert 'Неверные учетные данные' in data['message']

def test_login_nonexistent_user(client):
    """Тест входа несуществующего пользователя"""
    response = client.post('/login', json={
        'username': 'nonexistent',
        'password': 'password'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert 'Неверные учетные данные' in data['message']

def test_verify_token_success(client, sample_user_data):
    """Тест проверки валидного токена"""
    # Регистрация и вход
    client.post('/register', json=sample_user_data)
    login_response = client.post('/login', json={
        'username': sample_user_data['username'],
        'password': sample_user_data['password']
    })
    token = login_response.get_json()['token']
    
    # Проверка токена
    response = client.post('/verify', headers={
        'Authorization': f'Bearer {token}'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['valid'] is True
    assert data['user_id'] == sample_user_data['username']

def test_verify_token_missing(client):
    """Тест проверки токена без заголовка"""
    response = client.post('/verify')
    assert response.status_code == 401

def test_verify_token_invalid(client):
    """Тест проверки невалидного токена"""
    response = client.post('/verify', headers={
        'Authorization': 'Bearer invalid_token_here'
    })
    assert response.status_code == 401

def test_health_check(client):
    """Тест проверки здоровья сервиса"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['service'] == 'auth_service'


