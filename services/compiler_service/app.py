from flask import Flask, request, jsonify
import requests
import os
import subprocess
import tempfile
import shutil
from flasgger import Swagger, swag_from

app = Flask(__name__)

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
        "title": "Compiler Service API",
        "description": "API для компиляции и тестирования кода",
        "version": "1.0.0"
    }
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Простая база данных в памяти для тест-кейсов
test_cases_cache = {}

def get_problem_test_cases(problem_id):
    if problem_id in test_cases_cache:
        return test_cases_cache[problem_id]
    
    try:
        response = requests.get(f'{ADMIN_SERVICE_URL}/problems/{problem_id}')
        if response.status_code == 200:
            problem = response.json()
            test_cases = problem.get('test_cases', [])
            test_cases_cache[problem_id] = test_cases
            return test_cases
    except:
        pass
    
    return []

def run_python_code(code, input_data):
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                ['python', temp_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5
            )
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        finally:
            os.unlink(temp_file)
    except subprocess.TimeoutExpired:
        return {'stdout': '', 'stderr': 'Timeout', 'returncode': -1}
    except Exception as e:
        return {'stdout': '', 'stderr': str(e), 'returncode': -1}

@app.route('/health', methods=['GET'])
@swag_from({
    'tags': ['Health'],
    'summary': 'Проверка здоровья сервиса',
    'responses': {200: {'description': 'Сервис работает'}}
})
def health():
    return jsonify({'status': 'ok', 'service': 'compiler_service'})

@app.route('/compile', methods=['POST'])
@swag_from({
    'tags': ['Compiler'],
    'summary': 'Компиляция и тестирование кода',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'required': ['code'],
            'properties': {
                'submission_id': {'type': 'string'},
                'code': {'type': 'string', 'description': 'Код для компиляции'},
                'language': {'type': 'string', 'default': 'python'},
                'problem_id': {'type': 'string', 'description': 'ID задачи для получения тест-кейсов'}
            }
        }
    }],
    'responses': {
        200: {
            'description': 'Результат компиляции',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'enum': ['success', 'partial', 'failed', 'error']},
                    'result': {'type': 'string'},
                    'details': {'type': 'array'},
                    'passed': {'type': 'integer'},
                    'failed': {'type': 'integer'},
                    'total': {'type': 'integer'}
                }
            }
        },
        400: {'description': 'Код отсутствует'}
    }
})
def compile_and_test():
    data = request.get_json()
    submission_id = data.get('submission_id')
    code = data.get('code')
    language = data.get('language', 'python')
    problem_id = data.get('problem_id')
    
    if not code:
        return jsonify({'status': 'error', 'result': 'Код отсутствует'}), 400
    
    # Получаем тест-кейсы
    test_cases = get_problem_test_cases(problem_id) if problem_id else []
    
    if not test_cases:
        # Если тест-кейсов нет, просто проверяем синтаксис
        if language == 'python':
            try:
                compile(code, '<string>', 'exec')
                return jsonify({
                    'status': 'success',
                    'result': 'Код скомпилирован успешно (тест-кейсы отсутствуют)'
                }), 200
            except SyntaxError as e:
                return jsonify({
                    'status': 'error',
                    'result': f'Синтаксическая ошибка: {str(e)}'
                }), 200
    
    # Запускаем тесты
    passed = 0
    failed = 0
    results = []
    
    for i, test_case in enumerate(test_cases):
        input_data = test_case.get('input', '')
        expected_output = test_case.get('output', '').strip()
        
        if language == 'python':
            run_result = run_python_code(code, input_data)
            actual_output = run_result['stdout'].strip()
            
            if run_result['returncode'] != 0:
                results.append({
                    'test_case': i + 1,
                    'status': 'error',
                    'error': run_result['stderr']
                })
                failed += 1
            elif actual_output == expected_output:
                results.append({
                    'test_case': i + 1,
                    'status': 'passed'
                })
                passed += 1
            else:
                results.append({
                    'test_case': i + 1,
                    'status': 'failed',
                    'expected': expected_output,
                    'actual': actual_output
                })
                failed += 1
    
    if failed == 0 and passed > 0:
        status = 'success'
        result_message = f'Все тесты пройдены ({passed}/{len(test_cases)})'
    elif passed > 0:
        status = 'partial'
        result_message = f'Пройдено {passed} из {len(test_cases)} тестов'
    else:
        status = 'failed'
        result_message = f'Провалено {failed} тестов'
    
    return jsonify({
        'status': status,
        'result': result_message,
        'details': results,
        'passed': passed,
        'failed': failed,
        'total': len(test_cases)
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
