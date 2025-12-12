from flask import Flask, request, jsonify, send_from_directory
import requests
import os
import random
import logging
import time
from flasgger import Swagger, swag_from
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(service)s] - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logger = logging.LoggerAdapter(logger, {'service': 'user_service'})

app = Flask(__name__, static_folder='static', static_url_path='')

# Prometheus метрики
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['service', 'method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['service', 'method', 'endpoint']
)

# Middleware для логирования и метрик
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    endpoint = request.endpoint or 'unknown'
    
    # Логирование
    logger.info(
        f"{request.method} {request.path} - {response.status_code} - {duration:.3f}s",
        extra={
            'method': request.method,
            'endpoint': endpoint,
            'status_code': response.status_code,
            'duration': duration
        }
    )
    
    # Метрики
    http_requests_total.labels(
        service='user_service',
        method=request.method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()
    
    http_request_duration_seconds.labels(
        service='user_service',
        method=request.method,
        endpoint=endpoint
    ).observe(duration)
    
    return response

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth_service:5001')

# Простая база данных в памяти
users_profiles = {}
leaderboard = []
teams = {}

# Настройка Swagger
swagger_config = {
    "headers": [],
    "specs": [{
        "endpoint": "apispec",
        "route": "/apispec.json",
        "rule_filter": lambda rule: True,
        "model_filter": lambda tag: True,
    }],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api-docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "User Service API",
        "description": "API для управления пользователями, табло лидеров и командами",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT токен авторизации. Формат: Bearer {token}"
        }
    }
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

def verify_token(token):
    try:
        response = requests.post(
            f'{AUTH_SERVICE_URL}/verify',
            headers={'Authorization': f'Bearer {token}'}
        )
        if response.status_code == 200:
            return response.json().get('user_id')
        return None
    except:
        return None

@app.route('/health', methods=['GET'])
@swag_from({
    'tags': ['Health'],
    'summary': 'Проверка здоровья сервиса',
    'responses': {200: {'description': 'Сервис работает'}}
})
def health():
    return jsonify({'status': 'ok', 'service': 'user_service'})

@app.route('/profile/<user_id>', methods=['GET'])
@swag_from({
    'tags': ['Profile'],
    'summary': 'Получение профиля пользователя',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'user_id',
        'in': 'path',
        'type': 'string',
        'required': True,
        'description': 'Идентификатор пользователя'
    }],
    'responses': {
        200: {'description': 'Профиль пользователя'},
        401: {'description': 'Неавторизован'}
    }
})
def get_profile(user_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_token(token):
        return jsonify({'message': 'Неавторизован'}), 401
    
    profile = users_profiles.get(user_id, {
        'user_id': user_id,
        'rating': 0,
        'solved_problems': 0,
        'team_id': None
    })
    return jsonify(profile), 200

@app.route('/profile/<user_id>', methods=['PUT'])
@swag_from({
    'tags': ['Profile'],
    'summary': 'Обновление профиля пользователя',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'string',
            'required': True
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'rating': {'type': 'integer'},
                    'solved_problems': {'type': 'integer'},
                    'team_id': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {200: {'description': 'Профиль обновлен'}, 401: {'description': 'Неавторизован'}}
})
def update_profile(user_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    current_user = verify_token(token)
    if not current_user or current_user != user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    data = request.get_json()
    if user_id not in users_profiles:
        users_profiles[user_id] = {'user_id': user_id, 'rating': 0, 'solved_problems': 0}
    
    users_profiles[user_id].update(data)
    return jsonify(users_profiles[user_id]), 200

@app.route('/leaderboard', methods=['GET'])
@swag_from({
    'tags': ['Leaderboard'],
    'summary': 'Получение табло лидеров',
    'responses': {200: {'description': 'Табло лидеров'}}
})
def get_leaderboard():
    # Убрана проверка авторизации для демонстрации
    sorted_leaderboard = sorted(leaderboard, key=lambda x: x.get('rating', 0), reverse=True)
    return jsonify({'leaderboard': sorted_leaderboard}), 200

@app.route('/leaderboard/update', methods=['POST'])
@swag_from({
    'tags': ['Leaderboard'],
    'summary': 'Обновление табло лидеров',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'required': ['user_id', 'rating'],
            'properties': {
                'user_id': {'type': 'string'},
                'rating': {'type': 'integer'}
            }
        }
    }],
    'responses': {200: {'description': 'Табло обновлено'}}
})
def update_leaderboard():
    data = request.get_json()
    user_id = data.get('user_id')
    rating = data.get('rating', 0)
    
    entry = next((x for x in leaderboard if x['user_id'] == user_id), None)
    if entry:
        entry['rating'] = rating
    else:
        leaderboard.append({'user_id': user_id, 'rating': rating})
    
    return jsonify({'message': 'Обновлено'}), 200

@app.route('/teams', methods=['GET'])
@swag_from({
    'tags': ['Teams'],
    'summary': 'Получение списка команд',
    'responses': {200: {'description': 'Список команд'}}
})
def get_teams():
    # Убрана проверка авторизации для демонстрации
    return jsonify({'teams': list(teams.values())}), 200

@app.route('/teams', methods=['POST'])
@swag_from({
    'tags': ['Teams'],
    'summary': 'Создание новой команды',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'required': ['name'],
            'properties': {
                'name': {'type': 'string', 'description': 'Название команды'}
            }
        }
    }],
    'responses': {201: {'description': 'Команда создана'}, 400: {'description': 'Ошибка валидации'}}
})
def create_team():
    # Убрана проверка авторизации для демонстрации
    data = request.get_json()
    team_name = data.get('name')
    if not team_name:
        return jsonify({'message': 'Необходимо имя команды'}), 400
    
    team_id = f"team_{len(teams) + 1}"
    # Используем случайный user_id для демо
    user_id = f"user_{random.randint(1000, 9999)}"
    teams[team_id] = {
        'team_id': team_id,
        'name': team_name,
        'members': [user_id],
        'captain': user_id
    }
    
    return jsonify(teams[team_id]), 201

@app.route('/teams/<team_id>/join', methods=['POST'])
@swag_from({
    'tags': ['Teams'],
    'summary': 'Присоединение к команде',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'team_id',
        'in': 'path',
        'type': 'string',
        'required': True
    }],
    'responses': {200: {'description': 'Присоединен к команде'}, 401: {'description': 'Неавторизован'}, 404: {'description': 'Команда не найдена'}}
})
def join_team(team_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    if team_id not in teams:
        return jsonify({'message': 'Команда не найдена'}), 404
    
    if user_id not in teams[team_id]['members']:
        teams[team_id]['members'].append(user_id)
    
    return jsonify(teams[team_id]), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus метрики endpoint"""
    return generate_latest(REGISTRY), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# Статические файлы и главная страница - в конце, чтобы не перехватывать API endpoints
@app.route('/', methods=['GET'])
def index():
    """Главная страница с веб-интерфейсом"""
    try:
        import os
        static_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(static_path):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            return jsonify({'error': f'Static folder: {app.static_folder}, File not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error loading static file: {str(e)}, static_folder: {app.static_folder}'}), 404

if __name__ == '__main__':
    # Для Serverless Containers используем PORT из переменных окружения
    port = int(os.getenv('PORT', 5002))
    logger.info(f"Starting user_service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
