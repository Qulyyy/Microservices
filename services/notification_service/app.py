from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime
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
        "title": "Notification Service API",
        "description": "API для управления уведомлениями",
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

# Простая база данных в памяти
notifications = {}

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
    return jsonify({'status': 'ok', 'service': 'notification_service'})

@app.route('/notifications', methods=['POST'])
def create_notification():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    data = request.get_json()
    target_user_id = data.get('user_id')
    message = data.get('message')
    notification_type = data.get('type', 'info')
    
    if not target_user_id or not message:
        return jsonify({'message': 'Необходимы user_id и message'}), 400
    
    notification_id = f"notif_{len(notifications) + 1}"
    notification = {
        'notification_id': notification_id,
        'user_id': target_user_id,
        'message': message,
        'type': notification_type,
        'read': False,
        'created_at': datetime.now().isoformat()
    }
    
    if target_user_id not in notifications:
        notifications[target_user_id] = []
    notifications[target_user_id].append(notification)
    
    return jsonify(notification), 201

@app.route('/notifications/user/<user_id>', methods=['GET'])
def get_user_notifications(user_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    current_user = verify_token(token)
    if not current_user:
        return jsonify({'message': 'Неавторизован'}), 401
    
    # Пользователь может видеть только свои уведомления
    if current_user != user_id:
        return jsonify({'message': 'Доступ запрещен'}), 403
    
    user_notifications = notifications.get(user_id, [])
    unread_count = sum(1 for n in user_notifications if not n.get('read', False))
    
    return jsonify({
        'notifications': user_notifications,
        'unread_count': unread_count
    }), 200

@app.route('/notifications/<notification_id>/read', methods=['PUT'])
def mark_as_read(notification_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    for user_notifications in notifications.values():
        for notification in user_notifications:
            if notification['notification_id'] == notification_id:
                if notification['user_id'] != user_id:
                    return jsonify({'message': 'Доступ запрещен'}), 403
                notification['read'] = True
                return jsonify(notification), 200
    
    return jsonify({'message': 'Уведомление не найдено'}), 404

@app.route('/notifications/broadcast', methods=['POST'])
def broadcast_notification():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    data = request.get_json()
    message = data.get('message')
    notification_type = data.get('type', 'info')
    
    if not message:
        return jsonify({'message': 'Необходимо message'}), 400
    
    # Добавляем уведомление всем пользователям
    notification_id = f"notif_{len(notifications) + 1}"
    for user_key in notifications.keys():
        notification = {
            'notification_id': f"{notification_id}_{user_key}",
            'user_id': user_key,
            'message': message,
            'type': notification_type,
            'read': False,
            'created_at': datetime.now().isoformat()
        }
        notifications[user_key].append(notification)
    
    return jsonify({'message': 'Уведомление отправлено всем пользователям'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)

