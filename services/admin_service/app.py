from flask import Flask, request, jsonify
import requests
import os
from flasgger import Swagger, swag_from

app = Flask(__name__)

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
        "title": "Admin Service API",
        "description": "API для управления задачами и контестами (требуются права администратора)",
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

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth_service:5001')

problems = {}
contests = {}
admins = ['admin']

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

def is_admin(user_id):
    return user_id in admins

@app.route('/health', methods=['GET'])
@swag_from({
    'tags': ['Health'],
    'summary': 'Проверка здоровья сервиса',
    'responses': {200: {'description': 'Сервис работает'}}
})
def health():
    return jsonify({'status': 'ok', 'service': 'admin_service'})

@app.route('/problems', methods=['GET'])
@swag_from({
    'tags': ['Problems'],
    'summary': 'Получение списка задач',
    'security': [{'Bearer': []}],
    'responses': {200: {'description': 'Список задач'}, 401: {'description': 'Неавторизован'}}
})
def get_problems():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_token(token):
        return jsonify({'message': 'Неавторизован'}), 401
    
    return jsonify({'problems': list(problems.values())}), 200

@app.route('/problems/<problem_id>', methods=['GET'])
def get_problem(problem_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_token(token):
        return jsonify({'message': 'Неавторизован'}), 401
    
    if problem_id not in problems:
        return jsonify({'message': 'Задача не найдена'}), 404
    
    return jsonify(problems[problem_id]), 200

@app.route('/problems', methods=['POST'])
@swag_from({
    'tags': ['Problems'],
    'summary': 'Создание новой задачи (только админ)',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'required': ['title', 'description'],
            'properties': {
                'title': {'type': 'string'},
                'description': {'type': 'string'},
                'difficulty': {'type': 'string', 'enum': ['easy', 'medium', 'hard']},
                'test_cases': {'type': 'array', 'items': {'type': 'object'}},
                'time_limit': {'type': 'integer'},
                'memory_limit': {'type': 'integer'}
            }
        }
    }],
    'responses': {201: {'description': 'Задача создана'}, 403: {'description': 'Требуются права администратора'}}
})
def create_problem():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id or not is_admin(user_id):
        return jsonify({'message': 'Требуются права администратора'}), 403
    
    data = request.get_json()
    problem_id = data.get('problem_id') or f"problem_{len(problems) + 1}"
    
    problems[problem_id] = {
        'problem_id': problem_id,
        'title': data.get('title', ''),
        'description': data.get('description', ''),
        'difficulty': data.get('difficulty', 'medium'),
        'test_cases': data.get('test_cases', []),
        'time_limit': data.get('time_limit', 1),
        'memory_limit': data.get('memory_limit', 256),
        'created_by': user_id
    }
    
    return jsonify(problems[problem_id]), 201

@app.route('/problems/<problem_id>', methods=['PUT'])
def update_problem(problem_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id or not is_admin(user_id):
        return jsonify({'message': 'Требуются права администратора'}), 403
    
    if problem_id not in problems:
        return jsonify({'message': 'Задача не найдена'}), 404
    
    data = request.get_json()
    problems[problem_id].update(data)
    
    return jsonify(problems[problem_id]), 200

@app.route('/contests', methods=['GET'])
def get_contests():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_token(token):
        return jsonify({'message': 'Неавторизован'}), 401
    
    return jsonify({'contests': list(contests.values())}), 200

@app.route('/contests/<contest_id>', methods=['GET'])
def get_contest(contest_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_token(token):
        return jsonify({'message': 'Неавторизован'}), 401
    
    if contest_id not in contests:
        return jsonify({'message': 'Контест не найден'}), 404
    
    return jsonify(contests[contest_id]), 200

@app.route('/contests', methods=['POST'])
def create_contest():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id or not is_admin(user_id):
        return jsonify({'message': 'Требуются права администратора'}), 403
    
    data = request.get_json()
    contest_id = data.get('contest_id') or f"contest_{len(contests) + 1}"
    
    contests[contest_id] = {
        'contest_id': contest_id,
        'name': data.get('name', ''),
        'description': data.get('description', ''),
        'start_time': data.get('start_time', ''),
        'end_time': data.get('end_time', ''),
        'problems': data.get('problems', []),
        'created_by': user_id
    }
    
    return jsonify(contests[contest_id]), 201

@app.route('/contests/<contest_id>', methods=['PUT'])
def update_contest(contest_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id or not is_admin(user_id):
        return jsonify({'message': 'Требуются права администратора'}), 403
    
    if contest_id not in contests:
        return jsonify({'message': 'Контест не найден'}), 404
    
    data = request.get_json()
    contests[contest_id].update(data)
    
    return jsonify(contests[contest_id]), 200

@app.route('/contests/<contest_id>/problems/<problem_id>', methods=['POST'])
def add_problem_to_contest(contest_id, problem_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id or not is_admin(user_id):
        return jsonify({'message': 'Требуются права администратора'}), 403
    
    if contest_id not in contests:
        return jsonify({'message': 'Контест не найден'}), 404
    
    if problem_id not in problems:
        return jsonify({'message': 'Задача не найдена'}), 404
    
    if problem_id not in contests[contest_id]['problems']:
        contests[contest_id]['problems'].append(problem_id)
    
    return jsonify(contests[contest_id]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)

