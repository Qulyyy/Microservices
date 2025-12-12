"""
Альтернативный вариант: Producer создает очередь с уникальным именем
Это позволяет producer'у работать независимо от consumer'а
"""
import pika
import sys
import uuid

# Параметры подключения
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'guest'
RABBITMQ_PASSWORD = 'guest'

# Базовое название очереди
BASE_QUEUE_NAME = 'ikbo-27-22_contests_exclusive'

def send_message(message):
    """Отправка сообщения в очередь с уникальным именем"""
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials
            )
        )
        channel = connection.channel()
        
        # Создание очереди с уникальным именем для producer'а
        # Это позволяет producer'у работать независимо
        unique_queue_name = f"{BASE_QUEUE_NAME}_{uuid.uuid4().hex[:8]}"
        
        # Создание временной очереди (не эксклюзивной, чтобы consumer мог подключиться)
        channel.queue_declare(queue=unique_queue_name, exclusive=False, auto_delete=True)
        
        # Отправка сообщения
        channel.basic_publish(
            exchange='',
            routing_key=unique_queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
        
        print(f" [x] Отправлено сообщение: {message}")
        print(f" [x] Очередь: {unique_queue_name}")
        print(f" [*] Примечание: Это альтернативный вариант, не эксклюзивная очередь")
        
        connection.close()
        
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

if __name__ == '__main__':
    message = ' '.join(sys.argv[1:]) or "Привет из альтернативной очереди!"
    send_message(message)


