#!/bin/bash

# Скрипт для запуска всех тестов

echo "=== Запуск Unit-тестов ==="

echo "Auth Service Unit Tests..."
cd services/auth_service
pytest ./tests/unit -v
cd ../..

echo "User Service Unit Tests..."
cd services/user_service
pytest ./tests/unit -v
cd ../..

echo "Admin Service Unit Tests..."
cd services/admin_service
pytest ./tests/unit -v
cd ../..

echo "Compiler Service Unit Tests..."
cd services/compiler_service
pytest ./tests/unit -v
cd ../..

echo "=== Unit-тесты завершены ==="
echo ""
echo "Для запуска E2E тестов сначала запустите сервисы:"
echo "docker-compose up -d"


