#!/bin/bash

# Скрипт для запуска E2E тестов

echo "=== Запуск E2E тестов ==="

echo "Ожидание запуска сервисов..."
sleep 10

echo "Auth Service E2E Tests..."
cd services/auth_service
pytest ./tests/e2e -v
cd ../..

echo "User Service E2E Tests..."
cd services/user_service
pytest ./tests/e2e -v
cd ../..

echo "Admin Service E2E Tests..."
cd services/admin_service
pytest ./tests/e2e -v
cd ../..

echo "Compiler Service E2E Tests..."
cd services/compiler_service
pytest ./tests/e2e -v
cd ../..

echo "Submission Service E2E Tests..."
cd services/submission_service
pytest ./tests/e2e -v
cd ../..

echo "=== E2E тесты завершены ==="


