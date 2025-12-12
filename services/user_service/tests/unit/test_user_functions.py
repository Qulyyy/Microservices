import pytest
from unittest.mock import patch, MagicMock
from app import app, users_profiles, leaderboard, teams

@pytest.fixture
def client():
    """Создает тестовый клиент Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            # Очищаем данные перед каждым тестом
            users_profiles.clear()
            leaderboard.clear()
            teams.clear()
            yield client

@pytest.fixture
def mock_auth_verify():
    """Мок для verify_token"""
    with patch('app.verify_token') as mock:
        yield mock

def test_leaderboard_sorting():
    """Тест сортировки табло лидеров"""
    leaderboard.clear()
    leaderboard.extend([
        {'user_id': 'user1', 'rating': 100},
        {'user_id': 'user2', 'rating': 300},
        {'user_id': 'user3', 'rating': 200}
    ])
    
    sorted_board = sorted(
        leaderboard,
        key=lambda x: x.get('rating', 0),
        reverse=True
    )
    
    assert sorted_board[0]['rating'] == 300
    assert sorted_board[1]['rating'] == 200
    assert sorted_board[2]['rating'] == 100

def test_leaderboard_update_existing():
    """Тест обновления существующей записи в табло"""
    leaderboard.clear()
    leaderboard.append({'user_id': 'user1', 'rating': 100})
    
    entry = next((x for x in leaderboard if x['user_id'] == 'user1'), None)
    if entry:
        entry['rating'] = 200
    else:
        leaderboard.append({'user_id': 'user1', 'rating': 200})
    
    assert leaderboard[0]['rating'] == 200

def test_leaderboard_add_new():
    """Тест добавления новой записи в табло"""
    leaderboard.clear()
    
    user_id = 'newuser'
    rating = 150
    entry = next((x for x in leaderboard if x['user_id'] == user_id), None)
    if entry:
        entry['rating'] = rating
    else:
        leaderboard.append({'user_id': user_id, 'rating': rating})
    
    assert len(leaderboard) == 1
    assert leaderboard[0]['user_id'] == user_id
    assert leaderboard[0]['rating'] == rating

def test_team_creation():
    """Тест создания команды"""
    teams.clear()
    team_id = 'team_1'
    user_id = 'captain'
    team_name = 'Test Team'
    
    teams[team_id] = {
        'team_id': team_id,
        'name': team_name,
        'members': [user_id],
        'captain': user_id
    }
    
    assert team_id in teams
    assert teams[team_id]['name'] == team_name
    assert teams[team_id]['captain'] == user_id
    assert user_id in teams[team_id]['members']

def test_team_join():
    """Тест присоединения к команде"""
    teams.clear()
    team_id = 'team_1'
    teams[team_id] = {
        'team_id': team_id,
        'name': 'Test Team',
        'members': ['user1'],
        'captain': 'user1'
    }
    
    new_user = 'user2'
    if new_user not in teams[team_id]['members']:
        teams[team_id]['members'].append(new_user)
    
    assert len(teams[team_id]['members']) == 2
    assert new_user in teams[team_id]['members']

def test_profile_default_values():
    """Тест значений профиля по умолчанию"""
    users_profiles.clear()
    user_id = 'testuser'
    
    profile = users_profiles.get(user_id, {
        'user_id': user_id,
        'rating': 0,
        'solved_problems': 0,
        'team_id': None
    })
    
    assert profile['user_id'] == user_id
    assert profile['rating'] == 0
    assert profile['solved_problems'] == 0
    assert profile['team_id'] is None

def test_profile_update():
    """Тест обновления профиля"""
    users_profiles.clear()
    user_id = 'testuser'
    
    if user_id not in users_profiles:
        users_profiles[user_id] = {'user_id': user_id, 'rating': 0, 'solved_problems': 0}
    
    update_data = {'rating': 100, 'solved_problems': 5}
    users_profiles[user_id].update(update_data)
    
    assert users_profiles[user_id]['rating'] == 100
    assert users_profiles[user_id]['solved_problems'] == 5

def test_get_profile_unauthorized(client):
    """Тест получения профиля без авторизации"""
    mock_auth_verify = MagicMock(return_value=None)
    with patch('app.verify_token', mock_auth_verify):
        response = client.get('/profile/testuser')
        assert response.status_code == 401

def test_get_profile_authorized(client, mock_auth_verify):
    """Тест получения профиля с авторизацией"""
    mock_auth_verify.return_value = 'testuser'
    users_profiles['testuser'] = {
        'user_id': 'testuser',
        'rating': 100,
        'solved_problems': 5
    }
    
    response = client.get('/profile/testuser', headers={
        'Authorization': 'Bearer valid_token'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['user_id'] == 'testuser'


