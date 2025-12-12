from flask import Flask, request, jsonify
import requests
import os
import random
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
        "title": "Ad Service API",
        "description": "API для управления рекламой",
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

# Простая база данных в памяти для рекламы
ads = [
    {
        'ad_id': '1',
        'title': 'Курс по алгоритмам',
        'description': 'Изучите алгоритмы и структуры данных',
        'image_url': 'https://example.com/ad1.jpg',
        'link': 'https://example.com/course1',
        'category': 'education'
    },
    {
        'ad_id': '2',
        'title': 'Подготовка к собеседованиям',
        'description': 'Практикуйтесь на реальных задачах',
        'image_url': 'https://example.com/ad2.jpg',
        'link': 'https://example.com/course2',
        'category': 'career'
    },
    {
        'ad_id': '3',
        'title': 'Премиум подписка',
        'description': 'Получите доступ ко всем функциям',
        'image_url': 'https://example.com/ad3.jpg',
        'link': 'https://example.com/premium',
        'category': 'premium'
    }
]

ad_stats = {}

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
    return jsonify({'status': 'ok', 'service': 'ad_service'})

@app.route('/ads/random', methods=['GET'])
def get_random_ad():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    if not ads:
        return jsonify({'message': 'Реклама отсутствует'}), 404
    
    ad = random.choice(ads)
    
    # Статистика показов
    ad_id = ad['ad_id']
    if ad_id not in ad_stats:
        ad_stats[ad_id] = {'views': 0, 'clicks': 0}
    ad_stats[ad_id]['views'] += 1
    
    return jsonify(ad), 200

@app.route('/ads', methods=['GET'])
def get_all_ads():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_token(token):
        return jsonify({'message': 'Неавторизован'}), 401
    
    return jsonify({'ads': ads}), 200

@app.route('/ads', methods=['POST'])
def create_ad():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    data = request.get_json()
    ad_id = f"ad_{len(ads) + 1}"
    
    new_ad = {
        'ad_id': ad_id,
        'title': data.get('title', ''),
        'description': data.get('description', ''),
        'image_url': data.get('image_url', ''),
        'link': data.get('link', ''),
        'category': data.get('category', 'general')
    }
    
    ads.append(new_ad)
    ad_stats[ad_id] = {'views': 0, 'clicks': 0}
    
    return jsonify(new_ad), 201

@app.route('/ads/<ad_id>/click', methods=['POST'])
def track_click(ad_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    if ad_id not in ad_stats:
        return jsonify({'message': 'Реклама не найдена'}), 404
    
    ad_stats[ad_id]['clicks'] += 1
    
    return jsonify({'message': 'Клик зарегистрирован'}), 200

@app.route('/ads/stats', methods=['GET'])
def get_stats():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    return jsonify({'stats': ad_stats}), 200

@app.route('/ads/<ad_id>', methods=['DELETE'])
def delete_ad(ad_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Неавторизован'}), 401
    
    global ads
    ads = [ad for ad in ads if ad['ad_id'] != ad_id]
    
    if ad_id in ad_stats:
        del ad_stats[ad_id]
    
    return jsonify({'message': 'Реклама удалена'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True)

