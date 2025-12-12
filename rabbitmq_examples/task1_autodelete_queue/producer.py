"""
Задание 1.3: Producer для автоудаляемой очереди
auto_delete=True удаляет очередь, когда последний потребитель отключается
"""
import pika
import sys

# Параметры подключения
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'guest'
RABBITMQ_PASSWORD = 'guest'

# Название очереди
QUEUE_NAME = 'inbo-04_laptev_autodelete'

def send_message(message):
    """Отправка сообщения в автоудаляемую очередь"""
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
        
        # Создание автоудаляемой очереди
        # auto_delete=True удаляет очередь при отключении последнего потребителя
        channel.queue_declare(queue=QUEUE_NAME, auto_delete=True)
        
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
        
        print(f" [x] Отправлено сообщение: {message}")
        
        connection.close()
        
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

if __name__ == '__main__':
    message = ' '.join(sys.argv[1:]) or "Привет из автоудаляемой очереди!"
    send_message(message)


