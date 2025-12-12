# Исправление авторизации в Container Registry

## Проблема

Ошибка при отправке образа в Container Registry:
```
denied: Permission denied
```

## Причина

Неправильный метод авторизации в Container Registry. JSON ключи сервисного аккаунта нельзя использовать напрямую для авторизации в Docker.

## Решение

Использовать IAM токен для авторизации:

1. **Получить IAM токен** через YC CLI (который уже настроен с сервисным аккаунтом)
2. **Использовать токен** для авторизации в Docker

### Изменения в CI/CD

**Было:**
```yaml
cat /tmp/yc-keys.json | docker login \
  --username json_key \
  --password-stdin \
  cr.yandex
```

**Стало:**
```yaml
IAM_TOKEN=$(yc iam create-token)
echo "$IAM_TOKEN" | docker login \
  --username iam \
  --password-stdin \
  cr.yandex
```

## Проверка прав сервисного аккаунта

Убедитесь, что сервисный аккаунт имеет роль:
- `container-registry.images.pusher` - для отправки образов

## Альтернативный метод (если не работает)

Если IAM токен не работает, можно использовать OAuth токен:

```yaml
- name: Login to Yandex Container Registry
  run: |
    # Получаем OAuth токен
    OAUTH_TOKEN=$(yc config get token || echo "")
    if [ -z "$OAUTH_TOKEN" ]; then
      # Если нет токена, используем IAM токен
      IAM_TOKEN=$(yc iam create-token)
      echo "$IAM_TOKEN" | docker login --username iam --password-stdin cr.yandex
    else
      echo "$OAUTH_TOKEN" | docker login --username oauth --password-stdin cr.yandex
    fi
```

## Проверка

После исправления:
1. Сделайте commit и push
2. Проверьте выполнение CI/CD конвейера
3. Образ должен успешно отправиться в Container Registry

