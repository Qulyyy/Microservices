# Исправления CI/CD конвейера

## Проблема

Конвейер падал с ошибкой **exit code 127**, что означает "команда не найдена".

## Причины

1. **Команда `pytest` не найдена** - нужно использовать `python -m pytest`
2. **Команда `docker-compose` не найдена** - в новых версиях Docker используется `docker compose` (без дефиса)
3. **Отсутствие проверки существования тестов** - конвейер пытался запустить несуществующие тесты

## Исправления

### 1. Использование `python -m pytest` вместо `pytest`

**Было:**
```yaml
run: |
  pytest ./tests/unit -v
```

**Стало:**
```yaml
run: |
  python -m pytest ./tests/unit -v
```

### 2. Поддержка обоих вариантов Docker Compose

**Было:**
```yaml
run: |
  docker-compose up -d auth_service
```

**Стало:**
```yaml
run: |
  docker compose up -d auth_service || docker-compose up -d auth_service
```

### 3. Проверка существования тестов

Добавлена проверка перед запуском тестов:
```yaml
- name: Check if unit tests exist
  id: check_unit_tests
  working-directory: ./services/${{ matrix.service }}
  run: |
    if [ -d "./tests/unit" ] && [ "$(ls -A ./tests/unit/*.py 2>/dev/null)" ]; then
      echo "exists=true" >> $GITHUB_OUTPUT
    else
      echo "exists=false" >> $GITHUB_OUTPUT
    fi

- name: Run unit tests
  if: steps.check_unit_tests.outputs.exists == 'true'
  working-directory: ./services/${{ matrix.service }}
  run: |
    python -m pytest ./tests/unit -v --cov=. --cov-report=term-missing
```

### 4. Улучшенная установка зависимостей

Добавлена установка тестовых зависимостей:
```yaml
- name: Install dependencies
  working-directory: ./services/${{ matrix.service }}
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    # Установка зависимостей для тестирования
    pip install pytest pytest-cov requests || true
```

### 5. Правильная работа с рабочим каталогом

Добавлен переход в корневую директорию перед запуском docker compose:
```yaml
run: |
  cd ${{ github.workspace }}
  docker compose up -d auth_service || docker-compose up -d auth_service
```

## Результат

После исправлений конвейер должен:
- ✅ Правильно находить и запускать pytest
- ✅ Корректно работать с Docker Compose
- ✅ Пропускать тесты, если они не существуют
- ✅ Продолжать работу даже при частичных ошибках

## Проверка

После внесения изменений:
1. Сделайте commit и push
2. Проверьте выполнение конвейера в GitHub Actions
3. Убедитесь, что все тесты проходят успешно

