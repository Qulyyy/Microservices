from flask import Flask, request, jsonify
import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
        "title": "Email Service API",
        "description": "API для рассылки писем",
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

# Настройки SMTP (для реального использования настройте через переменные окружения)
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

# Лог отправленных писем (в продакшене использовать базу данных)
email_log = []

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

def send_email(to_email, subject, body):
    """Отправка email (в продакшене использовать реальный SMTP)"""
    try:
        if not SMTP_USER or not SMTP_PASSWORD:
            # В режиме разработки просто логируем
            email_log.append({
                'to': to_email,
                'subject': subject,
                'body': body,
                'status': 'logged (SMTP not configured)'
            })
            return True
        
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        email_log.append({
            'to': to_email,
            'subject': subject,
            'status': 'sent'
        })
        return True
    except Exception as e:
        email_log.append({
            'to': to_email,
            'subject': subject,
            'status': f'error: {str(e)}'
        })
        return False

@app.route('/health', methods=['GET'])
@swag_from({
    'tags': ['Health'],
    'summary': 'Проверка здоровья сервиса',
    'responses': {200: {'description': 'Сервис работает'}}
})
def health():
    return jsonify({'status': 'ok', 'service': 'email_service'})

@app.route('/send', methods=['POST'])
def send_email_endpoint():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    data = request.get_json()
    to_email = data.get('to')
    subject = data.get('subject')
    body = data.get('body')
    
    if not to_email or not subject or not body:
        return jsonify({'message': 'Необходимы to, subject и body'}), 400
    
    success = send_email(to_email, subject, body)
    
    if success:
        return jsonify({'message': 'Письмо отправлено'}), 200
    else:
        return jsonify({'message': 'Ошибка при отправке письма'}), 500

@app.route('/send/bulk', methods=['POST'])
def send_bulk_email():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    data = request.get_json()
    recipients = data.get('recipients', [])
    subject = data.get('subject')
    body = data.get('body')
    
    if not recipients or not subject or not body:
        return jsonify({'message': 'Необходимы recipients, subject и body'}), 400
    
    results = []
    for recipient in recipients:
        success = send_email(recipient, subject, body)
        results.append({'email': recipient, 'status': 'sent' if success else 'failed'})
    
    return jsonify({'results': results}), 200

@app.route('/send/welcome', methods=['POST'])
def send_welcome_email():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    data = request.get_json()
    to_email = data.get('to')
    username = data.get('username', 'Пользователь')
    
    if not to_email:
        return jsonify({'message': 'Необходим email'}), 400
    
    subject = 'Добро пожаловать!'
    body = f'''
Здравствуйте, {username}!

Добро пожаловать на нашу платформу!

Мы рады, что вы присоединились к нам. Начните решать задачи и улучшайте свои навыки программирования.

Удачи!
Команда платформы
    '''
    
    success = send_email(to_email, subject, body)
    
    if success:
        return jsonify({'message': 'Приветственное письмо отправлено'}), 200
    else:
        return jsonify({'message': 'Ошибка при отправке письма'}), 500

@app.route('/logs', methods=['GET'])
def get_email_logs():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    return jsonify({'logs': email_log[-100:]}), 200  # Последние 100 записей

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=True)

