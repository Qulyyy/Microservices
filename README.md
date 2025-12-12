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

### 1. Запуск всех сервисов (включая RabbitMQ и Observability)

```bash
docker-compose up --build
```

Эта команда запустит:
- Все 8 микросервисов
- RabbitMQ брокер сообщений (порт 5672, веб-интерфейс 15672)
- **Loki** - система логирования (порт 3100)
- **Promtail** - агент сбора логов
- **Prometheus** - система мониторинга (порт 9090)
- **Grafana** - визуализация (порт 3000)

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

## Observability (Практическая работа №10)

### Доступ к интерфейсам

**Grafana:**
- URL: http://localhost:3000
- Логин: `admin`
- Пароль: `admin`

**Prometheus:**
- URL: http://localhost:9090

**Loki:**
- URL: http://localhost:3100 (API)

### Просмотр метрик

Каждый сервис экспортирует метрики Prometheus на endpoint `/metrics`:

```bash
# Метрики auth_service
curl http://localhost:5001/metrics

# Метрики user_service
curl http://localhost:5002/metrics
```

### Использование Grafana

1. **Просмотр логов:**
   - Откройте Grafana → Explore
   - Выберите источник данных **Loki**
   - Введите запрос: `{container="auth_service"}`

2. **Просмотр метрик:**
   - Откройте Grafana → Explore
   - Выберите источник данных **Prometheus**
   - Введите запрос: `rate(http_requests_total[5m])`

Подробная инструкция: [ПРАКТИКА_10_OBSERVABILITY.md](ПРАКТИКА_10_OBSERVABILITY.md)

## API Документация

Каждый сервис имеет Swagger документацию:

- **auth_service**: http://localhost:5001/api-docs
- **user_service**: http://localhost:5002/api-docs
- **admin_service**: http://localhost:5003/api-docs
- И так далее...

## Веб-интерфейс

**user_service** имеет веб-интерфейс:
- URL: http://localhost:5002

## Тестирование

В проекте реализованы unit-тесты и компонентные (E2E) тесты для основных сервисов. Тесты автоматически запускаются в CI/CD конвейере.

## CI/CD

В проекте настроены конвейеры непрерывной интеграции и доставки:

- **Автоматическое тестирование** при каждом push и pull request
- **Доставка в DockerHub** для `auth_service` (при push в main/master)
- **Развёртывание в Яндекс.Облако** для `user_service` (Serverless Containers)

## RabbitMQ

Примеры работы с RabbitMQ находятся в папке `rabbitmq_examples/`.

Подробная инструкция: [rabbitmq_examples/README.md](rabbitmq_examples/README.md)

## Структура проекта

```
.
├── services/              # Микросервисы
│   ├── auth_service/
│   ├── user_service/
│   ├── admin_service/
│   └── ...
├── observability/         # Конфигурация observability
│   ├── promtail-config.yml
│   ├── prometheus-config.yml
│   └── grafana/
├── rabbitmq_examples/     # Примеры работы с RabbitMQ
├── docker-compose.yml     # Основной compose файл
└── README.md
```

## Дополнительная информация

- **API Документация**: Swagger доступен на `/api-docs` каждого сервиса
- **Логирование**: Централизованное логирование через Loki
- **Мониторинг**: Метрики собираются через Prometheus
- **Визуализация**: Дашборды в Grafana
