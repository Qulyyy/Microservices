#!/bin/bash
# Скрипт для запуска тестов через Docker

echo "=== Запуск тестов через Docker ==="

echo "Unit-тесты..."
docker-compose run --rm auth_service python -m pytest ./tests/unit -v

echo "E2E тесты (требуют запущенных сервисов)..."
echo "Сначала запустите: docker-compose up -d"
docker-compose exec auth_service python -m pytest ./tests/e2e -v


