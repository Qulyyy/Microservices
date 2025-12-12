# CI/CD Конвейеры

## Настройка секретов

Перед использованием CI/CD конвейеров необходимо настроить секреты в GitHub.

### Переход к настройке секретов

1. Откройте ваш репозиторий на GitHub
2. Перейдите в **Settings** (Настройки)
3. Выберите **Secrets and variables** → **Actions**
4. Нажмите **New repository secret**

### Список необходимых секретов

#### Для DockerHub (auth_service)

| Секрет | Описание | Где получить |
|--------|----------|-------------|
| `DOCKERHUB_USERNAME` | Логин на DockerHub | https://hub.docker.com |
| `DOCKERHUB_TOKEN` | Personal Access Token | DockerHub → Account Settings → Security |

#### Для Яндекс.Облако (user_service)

| Секрет | Описание | Где получить |
|--------|----------|-------------|
| `YC_KEYS` | JSON ключи сервисного аккаунта | Яндекс.Облако → Сервисные аккаунты → Создать ключ |
| `YC_REGISTRY_ID` | ID реестра контейнеров | Container Registry → ID реестра |
| `YC_SA_ID` | ID сервисного аккаунта | Сервисные аккаунты → ID аккаунта |
| `YC_CONTAINER_NAME` | Имя контейнера | Serverless Containers → Имя контейнера |
| `YC_FOLDER_ID` | ID каталога | Каталог → ID каталога |
| `AUTH_SERVICE_URL` | URL сервиса авторизации | Опционально, по умолчанию: `http://auth-service:5001` |

## Быстрая настройка

### 1. DockerHub

```bash
# Создайте токен на https://hub.docker.com/settings/security
# Добавьте секреты:
# DOCKERHUB_USERNAME = ваш_логин
# DOCKERHUB_TOKEN = ваш_токен
```

### 2. Яндекс.Облако

```bash
# 1. Создайте Container Registry
# 2. Создайте сервисный аккаунт с ролями:
#    - container-registry.images.pusher
#    - serverless.containers.deployer
# 3. Создайте авторизованный ключ (JSON)
# 4. Создайте Serverless Container
# 5. Добавьте все секреты в GitHub
```

## Проверка работы

После настройки секретов:

1. Сделайте commit и push в ветку `main` или `master`
2. Перейдите в **Actions** на GitHub
3. Увидите запуск конвейера
4. Проверьте выполнение всех jobs

## Структура конвейера

```
┌─────────┐
│  Push   │
└────┬────┘
     │
     ▼
┌─────────┐
│  Test   │ ──► Unit тесты + E2E тесты
└────┬────┘
     │
     ├─────────────────┬─────────────────┐
     ▼                 ▼                 ▼
┌─────────────┐  ┌──────────────┐  ┌─────────────┐
│  DockerHub  │  │ Yandex Cloud │  │ Other Build│
│ (auth_svc)  │  │ (user_svc)   │  │            │
└─────────────┘  └──────────────┘  └─────────────┘
```

## Логи конвейера

Все логи доступны в разделе **Actions** на GitHub. Можно просмотреть:
- Вывод каждого шага
- Ошибки компиляции
- Результаты тестов
- Статус развёртывания

