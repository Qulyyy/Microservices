# PowerShell скрипт для запуска тестов через Docker

Write-Host "=== Запуск тестов через Docker ===" -ForegroundColor Green

Write-Host "`nUnit-тесты..." -ForegroundColor Yellow
docker-compose run --rm auth_service python -m pytest ./tests/unit -v

Write-Host "`nE2E тесты (требуют запущенных сервисов)..." -ForegroundColor Yellow
Write-Host "Сначала запустите: docker-compose up -d" -ForegroundColor Cyan
docker-compose exec auth_service python -m pytest ./tests/e2e -v


