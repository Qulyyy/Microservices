from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime
from flasgger import Swagger, swag_from

app = Flask(__name__)

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth_service:5001')
COMPILER_SERVICE_URL = os.getenv('COMPILER_SERVICE_URL', 'http://compiler_service:5005')
ADMIN_SERVICE_URL = os.getenv('ADMIN_SERVICE_URL', 'http://admin_service:5003')

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
        "title": "Submission Service API",
        "description": "API для управления сабмишенами (решениями задач)",
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

# Простая база данных в памяти
submissions = {}

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
    return jsonify({'status': 'ok', 'service': 'submission_service'})

@app.route('/submissions', methods=['POST'])
@swag_from({
    'tags': ['Submissions'],
    'summary': 'Создание сабмишена',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'required': ['problem_id', 'code'],
            'properties': {
                'problem_id': {'type': 'string'},
                'code': {'type': 'string'},
                'language': {'type': 'string', 'default': 'python'}
            }
        }
    }],
    'responses': {201: {'description': 'Сабмишн создан'}, 400: {'description': 'Ошибка валидации'}, 401: {'description': 'Неавторизован'}}
})
def create_submission():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    data = request.get_json()
    problem_id = data.get('problem_id')
    code = data.get('code')
    language = data.get('language', 'python')
    
    if not problem_id or not code:
        return jsonify({'message': 'Необходимы problem_id и code'}), 400
    
    submission_id = f"sub_{len(submissions) + 1}"
    submission = {
        'submission_id': submission_id,
        'user_id': user_id,
        'problem_id': problem_id,
        'code': code,
        'language': language,
        'status': 'pending',
        'result': None,
        'created_at': datetime.now().isoformat()
    }
    
    submissions[submission_id] = submission
    
    # Отправляем на компиляцию
    try:
        compile_response = requests.post(
            f'{COMPILER_SERVICE_URL}/compile',
            json={
                'submission_id': submission_id,
                'code': code,
                'language': language,
                'problem_id': problem_id
            }
        )
        if compile_response.status_code == 200:
            result = compile_response.json()
            submission['status'] = result.get('status', 'error')
            submission['result'] = result.get('result')
    except Exception as e:
        submission['status'] = 'error'
        submission['result'] = str(e)
    
    return jsonify(submission), 201

@app.route('/submissions/<submission_id>', methods=['GET'])
@swag_from({
    'tags': ['Submissions'],
    'summary': 'Получение сабмишена по ID',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'submission_id',
        'in': 'path',
        'type': 'string',
        'required': True
    }],
    'responses': {200: {'description': 'Сабмишн найден'}, 401: {'description': 'Неавторизован'}, 403: {'description': 'Доступ запрещен'}, 404: {'description': 'Не найден'}}
})
def get_submission(submission_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    if submission_id not in submissions:
        return jsonify({'message': 'Сабмишн не найден'}), 404
    
    submission = submissions[submission_id]
    if submission['user_id'] != user_id:
        return jsonify({'message': 'Доступ запрещен'}), 403
    
    return jsonify(submission), 200

@app.route('/submissions/user/<user_id>', methods=['GET'])
@swag_from({
    'tags': ['Submissions'],
    'summary': 'Получение сабмишенов пользователя',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'user_id',
        'in': 'path',
        'type': 'string',
        'required': True
    }],
    'responses': {200: {'description': 'Список сабмишенов'}, 401: {'description': 'Неавторизован'}, 403: {'description': 'Доступ запрещен'}}
})
def get_user_submissions(user_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    current_user = verify_token(token)
    if not current_user:
        return jsonify({'message': 'Неавторизован'}), 401
    
    if current_user != user_id:
        return jsonify({'message': 'Доступ запрещен'}), 403
    
    user_submissions = [s for s in submissions.values() if s['user_id'] == user_id]
    return jsonify({'submissions': user_submissions}), 200

@app.route('/submissions/problem/<problem_id>', methods=['GET'])
@swag_from({
    'tags': ['Submissions'],
    'summary': 'Получение сабмишенов по задаче',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'problem_id',
        'in': 'path',
        'type': 'string',
        'required': True
    }],
    'responses': {200: {'description': 'Список сабмишенов'}, 401: {'description': 'Неавторизован'}}
})
def get_problem_submissions(problem_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    problem_submissions = [s for s in submissions.values() if s['problem_id'] == problem_id]
    return jsonify({'submissions': problem_submissions}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
