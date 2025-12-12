# Система микросервисов

Система состоит из 8 микросервисов на Python:

1. **auth_service** (порт 5001) - Регистрация и авторизация
2. **user_service** (порт 5002) - Управление пользователями, табло лидеров, команды
3. **admin_service** (порт 5003) - Админ-панель, управление задачами и контестами
4. **submission_service** (порт 5004) - Управление сабмишенами (решениями задач)
5. **compiler_service** (порт 5005) - Компиляция и тестирование кода
6. **notification_service** (порт 5006) - Система уведомлений
7. **ad_service** (порт 5007) - Сервис для показа рекламы
8. **email_service** (порт 5008) - Рассылка писем на почту

## Требования

- Docker
- Docker Compose
- Python 3.11+ (для запуска примеров RabbitMQ)

## Запуск системы

### 1. Запуск всех сервисов (включая RabbitMQ)

```bash
docker-compose up --build
```

Эта команда запустит:
- Все 8 микросервисов
- RabbitMQ брокер сообщений (порт 5672, веб-интерфейс 15672)

Эта команда:
- Соберет Docker-образы для всех сервисов
- Запустит все 8 микросервисов
- Создаст сеть для взаимодействия между сервисами

### 2. Запуск в фоновом режиме

```bash
docker-compose up -d --build
```

### 3. Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f auth_service
```

### 4. Остановка системы

```bash
docker-compose down
```

### 5. Перезапуск конкретного сервиса

```bash
docker-compose restart auth_service
```

## Проверка работоспособности

После запуска можно проверить здоровье каждого сервиса:

```bash
# Auth Service
curl http://localhost:5001/health

# User Service
curl http://localhost:5002/health

# Admin Service
curl http://localhost:5003/health

# Submission Service
curl http://localhost:5004/health

# Compiler Service
curl http://localhost:5005/health

# Notification Service
curl http://localhost:5006/health

# Ad Service
curl http://localhost:5007/health

# Email Service
curl http://localhost:5008/health
```

## Примеры использования API

### Регистрация пользователя

```bash
curl -X POST http://localhost:5001/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123",
    "email": "test@example.com"
  }'
```

### Авторизация

```bash
curl -X POST http://localhost:5001/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

Сохраните полученный токен для дальнейших запросов.

### Создание задачи (требуются права администратора)

```bash
curl -X POST http://localhost:5003/problems \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Сумма двух чисел",
    "description": "Найдите сумму двух чисел",
    "difficulty": "easy",
    "test_cases": [
      {"input": "2 3", "output": "5"},
      {"input": "10 20", "output": "30"}
    ]
  }'
```

### Отправка решения

```bash
curl -X POST http://localhost:5004/submissions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "problem_id": "problem_1",
    "code": "a, b = map(int, input().split())\nprint(a + b)",
    "language": "python"
  }'
```

## Настройка Email сервиса

Для работы email сервиса в продакшене настройте переменные окружения в `docker-compose.yml` или создайте файл `.env`:

```
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

В режиме разработки email сервис будет только логировать письма без реальной отправки.

## Структура проекта

```
.
├── docker-compose.yml
├── README.md
└── services/
    ├── auth_service/
    │   ├── app.py
    │   ├── requirements.txt
    │   └── Dockerfile
    ├── user_service/
    │   ├── app.py
    │   ├── requirements.txt
    │   └── Dockerfile
    ├── admin_service/
    │   ├── app.py
    │   ├── requirements.txt
    │   └── Dockerfile
    ├── submission_service/
    │   ├── app.py
    │   ├── requirements.txt
    │   └── Dockerfile
    ├── compiler_service/
    │   ├── app.py
    │   ├── requirements.txt
    │   └── Dockerfile
    ├── notification_service/
    │   ├── app.py
    │   ├── requirements.txt
    │   └── Dockerfile
    ├── ad_service/
    │   ├── app.py
    │   ├── requirements.txt
    │   └── Dockerfile
    └── email_service/
        ├── app.py
        ├── requirements.txt
        └── Dockerfile
```

## Документация API

### Swagger UI (Интерактивная документация)

После запуска сервисов, Swagger UI доступен для каждого сервиса:

- **Auth Service:** http://localhost:5001/api-docs
- **User Service:** http://localhost:5002/api-docs
- **Admin Service:** http://localhost:5003/api-docs
- **Submission Service:** http://localhost:5004/api-docs
- **Compiler Service:** http://localhost:5005/api-docs
- **Notification Service:** http://localhost:5006/api-docs
- **Ad Service:** http://localhost:5007/api-docs
- **Email Service:** http://localhost:5008/api-docs

Подробная инструкция по использованию Swagger UI находится в файле [SWAGGER_README.md](SWAGGER_README.md).

### Текстовая документация

Полная документация REST API для всех микросервисов находится в файле [ПРАКТИКА_6_API_ДОКУМЕНТАЦИЯ.md](ПРАКТИКА_6_API_ДОКУМЕНТАЦИЯ.md).

Документация включает:
- Описание всех endpoints для 8 микросервисов
- Структуру запросов и ответов
- Примеры использования
- Коды ответов HTTP
- Требования к авторизации

## CI/CD

В проекте настроены конвейеры непрерывной интеграции и доставки:

- **Автоматическое тестирование** при каждом push и pull request
- **Доставка в DockerHub** для `auth_service` (при push в main/master)
- **Развёртывание в Яндекс.Облако** для `user_service` (Serverless Containers)

**Документация:**
- [ПРАКТИКА_7_ИНСТРУКЦИЯ.md](ПРАКТИКА_7_ИНСТРУКЦИЯ.md) - полная инструкция по настройке
- [НАСТРОЙКА_СЕКРЕТОВ.md](НАСТРОЙКА_СЕКРЕТОВ.md) - настройка секретов GitHub
- [ПРОВЕРКА_CI_CD.md](ПРОВЕРКА_CI_CD.md) - как проверить результаты работы CI/CD

## Тестирование

В проекте реализованы unit-тесты и компонентные (E2E) тесты для основных сервисов. Тесты автоматически запускаются в CI/CD конвейере.

### Быстрый запуск тестов

```bash
# Unit-тесты для auth_service
cd services/auth_service
pytest ./tests/unit -v

# E2E тесты (требуют запущенных сервисов)
docker-compose up -d auth_service
sleep 10
pytest ./tests/e2e -v
```

### CI/CD

Тесты автоматически запускаются в GitHub Actions при каждом push. См. `.github/workflows/ci-cd.yml`.

## RabbitMQ

В проекте интегрирован RabbitMQ для асинхронного межсервисного взаимодействия.

**Доступ:**
- AMQP порт: `localhost:5672`
- Web интерфейс: http://localhost:15672
- Логин: `guest`
- Пароль: `guest`

**Примеры использования:**
- Примеры работы с RabbitMQ находятся в директории `rabbitmq_examples/`
- Подробная инструкция: [ПРАКТИКА_5_ИНСТРУКЦИЯ.md](ПРАКТИКА_5_ИНСТРУКЦИЯ.md)

**Типы реализованных взаимодействий:**
- Эксклюзивные очереди
- Устойчивые очереди
- Автоудаляемые очереди
- Fanout обменники
- Direct обменники
- Topic обменники

## Примечания

- Все сервисы используют простую базу данных в памяти для демонстрации. В продакшене рекомендуется использовать PostgreSQL, MongoDB или другую БД.
- Токены JWT имеют срок действия 24 часа.
- Для продакшена необходимо настроить реальные SMTP-серверы для email сервиса.
- Рекомендуется добавить rate limiting и другие меры безопасности.
- Тесты покрывают основные функции сервисов: auth_service, user_service, admin_service, compiler_service, submission_service.
- RabbitMQ используется для асинхронного взаимодействия между микросервисами.

