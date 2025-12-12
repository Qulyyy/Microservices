import pytest
import subprocess
import tempfile
import os
import sys

# Добавляем путь к модулю app
current_dir = os.path.dirname(os.path.abspath(__file__))
service_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, service_dir)

from app import run_python_code

def test_run_python_code_success():
    """Тест успешного выполнения Python кода"""
    code = "print('Hello, World!')"
    result = run_python_code(code, "")
    
    assert result['returncode'] == 0
    assert 'Hello, World!' in result['stdout']

def test_run_python_code_with_input():
    """Тест выполнения Python кода с входными данными"""
    code = "a, b = map(int, input().split())\nprint(a + b)"
    input_data = "5 3"
    result = run_python_code(code, input_data)
    
    assert result['returncode'] == 0
    assert result['stdout'].strip() == "8"

def test_run_python_code_syntax_error():
    """Тест обработки синтаксической ошибки"""
    code = "print('unclosed string"
    result = run_python_code(code, "")
    
    assert result['returncode'] != 0
    assert 'error' in result['stderr'].lower() or 'syntax' in result['stderr'].lower()

def test_compile_python_syntax():
    """Тест компиляции Python кода"""
    code = "x = 5\ny = 10\nprint(x + y)"
    try:
        compile(code, '<string>', 'exec')
        assert True
    except SyntaxError:
        assert False

