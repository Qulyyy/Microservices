"""
Задание 1.2: Producer для очереди, сохраняемой при перезапуске RabbitMQ
durable=True делает очередь устойчивой к перезапуску сервера
"""
import pika
import sys

# Параметры подключения
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'guest'
RABBITMQ_PASSWORD = 'guest'

# Название очереди
QUEUE_NAME = 'inbo-04_laptev_durable'

def send_message(message):
    """Отправка сообщения в устойчивую очередь"""
    try:
        # Подключение к RabbitMQ
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials
            )
        )
        channel = connection.channel()
        
        # Создание устойчивой очереди
        # durable=True делает очередь устойчивой к перезапуску
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        
        # Отправка сообщения с сохранением на диск
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Сообщение сохраняется на диск
            )
        )
        
        print(f" [x] Отправлено сообщение: {message}")
        
        connection.close()
        
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

if __name__ == '__main__':
    message = ' '.join(sys.argv[1:]) or "Привет из устойчивой очереди!"
    send_message(message)


