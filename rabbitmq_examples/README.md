# Примеры работы с RabbitMQ

Примеры для практической работы №5 по брокеру сообщений.

## Быстрый старт

1. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Запустите RabbitMQ:**
   ```bash
   docker-compose up -d rabbitmq
   ```
   Или используйте учебный сервер (измените параметры в коде).

3. **Запустите примеры:**

### Задание 1: Простейшее взаимодействие

**Эксклюзивная очередь:**
```bash
# Терминал 1
cd task1_exclusive_queue
python consumer.py

# Терминал 2
python producer.py "Тестовое сообщение"
```

**Устойчивая очередь:**
```bash
cd task1_durable_queue
python consumer.py  # в одном терминале
python producer.py "Сообщение"  # в другом
```

**Автоудаляемая очередь:**
```bash
cd task1_autodelete_queue
python consumer.py  # в одном терминале
python producer.py "Сообщение"  # в другом
```

### Задание 2: Взаимодействие с нагрузкой

**Fanout (символ #):**
```bash
cd task2_fanout
python consumer.py #2  # в одном терминале
python producer.py "Сообщение" #1  # в другом
```

**Direct (символ *):**
```bash
cd task2_direct
python consumer.py info *1  # в одном терминале
python producer.py "Сообщение" info *1  # в другом
```

**Topic (символ -):**
```bash
cd task2_topic
python consumer.py "stock.*.usd" -1  # в одном терминале
python producer.py "Акции США" stock.usa.usd -1  # в другом
```

## Структура

- `task1_*` - Задание 1 (простейшее взаимодействие)
- `task2_*` - Задание 2 (взаимодействие с нагрузкой)

## Параметры подключения

По умолчанию используется локальный RabbitMQ:
- Хост: `localhost`
- Порт: `5672`
- Логин: `guest`
- Пароль: `guest`

Для использования учебного сервера измените параметры в файлах:
- Хост: `51.250.26.59`
- Порт: `5672`
- Логин: `guest`
- Пароль: `guest123`


