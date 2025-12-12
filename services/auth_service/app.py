from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from functools import wraps
from flasgger import Swagger, swag_from

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Настройка Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api-docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Auth Service API",
        "description": "API для регистрации и авторизации пользователей",
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

# Простая база данных в памяти (в продакшене использовать PostgreSQL)
users_db = {}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Токен отсутствует'}), 401
        try:
            token = token.split(' ')[1] if token.startswith('Bearer ') else token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['user_id']
        except:
            return jsonify({'message': 'Неверный токен'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/health', methods=['GET'])
@swag_from({
    'tags': ['Health'],
    'summary': 'Проверка здоровья сервиса',
    'responses': {
        200: {
            'description': 'Сервис работает',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'ok'},
                    'service': {'type': 'string', 'example': 'auth_service'}
                }
            }
        }
    }
})
def health():
    return jsonify({'status': 'ok', 'service': 'auth_service'})

@app.route('/register', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Регистрация нового пользователя',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['username', 'password', 'email'],
                'properties': {
                    'username': {
                        'type': 'string',
                        'description': 'Уникальное имя пользователя',
                        'example': 'testuser'
                    },
                    'password': {
                        'type': 'string',
                        'description': 'Пароль пользователя',
                        'example': 'password123'
                    },
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'description': 'Электронная почта',
                        'example': 'test@example.com'
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Пользователь успешно зарегистрирован',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Пользователь успешно зарегистрирован'}
                }
            }
        },
        400: {
            'description': 'Ошибка валидации',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        }
    }
})
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password or not email:
        return jsonify({'message': 'Необходимы username, password и email'}), 400
    
    if username in users_db:
        return jsonify({'message': 'Пользователь уже существует'}), 400
    
    users_db[username] = {
        'password_hash': generate_password_hash(password),
        'email': email,
        'created_at': datetime.datetime.now().isoformat()
    }
    
    return jsonify({'message': 'Пользователь успешно зарегистрирован'}), 201

@app.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Авторизация пользователя',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['username', 'password'],
                'properties': {
                    'username': {
                        'type': 'string',
                        'description': 'Имя пользователя',
                        'example': 'testuser'
                    },
                    'password': {
                        'type': 'string',
                        'description': 'Пароль пользователя',
                        'example': 'password123'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Успешная авторизация',
            'schema': {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string', 'description': 'JWT токен'},
                    'user_id': {'type': 'string', 'example': 'testuser'}
                }
            }
        },
        400: {
            'description': 'Недостаточно данных'
        },
        401: {
            'description': 'Неверные учетные данные'
        }
    }
})
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Необходимы username и password'}), 400
    
    user = users_db.get(username)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'message': 'Неверные учетные данные'}), 401
    
    token = jwt.encode({
        'user_id': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({'token': token, 'user_id': username}), 200

@app.route('/verify', methods=['POST'])
@token_required
@swag_from({
    'tags': ['Auth'],
    'summary': 'Проверка валидности токена',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'Токен валиден',
            'schema': {
                'type': 'object',
                'properties': {
                    'valid': {'type': 'boolean', 'example': True},
                    'user_id': {'type': 'string', 'example': 'testuser'}
                }
            }
        },
        401: {
            'description': 'Токен отсутствует или неверен'
        }
    }
})
def verify_token(current_user):
    return jsonify({'valid': True, 'user_id': current_user}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

