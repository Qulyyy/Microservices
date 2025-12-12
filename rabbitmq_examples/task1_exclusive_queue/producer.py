"""
Задание 1.1: Producer для эксклюзивной очереди
Эксклюзивная очередь доступна только для текущего соединения и удаляется при закрытии соединения
"""
import pika
import sys

# Параметры подключения
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'guest'
RABBITMQ_PASSWORD = 'guest'

# Название очереди в формате <группа>_<фамилия>
QUEUE_NAME = 'inbo-04_laptev_exclusive'

def send_message(message):
    """Отправка сообщения в эксклюзивную очередь"""
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
        
        # Для эксклюзивной очереди producer не создает очередь
        # Он только отправляет сообщения в очередь, которая уже создана consumer'ом
        # Если очередь не существует, сообщение будет потеряно
        # Это особенность эксклюзивных очередей - они доступны только одному соединению
        
        # Отправка сообщения
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Сообщение сохраняется на диск
            )
        )
        
        print(f" [x] Отправлено сообщение: {message}")
        print(f" [*] Примечание: Убедитесь, что consumer запущен и создал очередь")
        
        connection.close()
        
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")
        print(f" [*] Убедитесь, что consumer запущен и создал эксклюзивную очередь")

if __name__ == '__main__':
    message = ' '.join(sys.argv[1:]) or "Привет из эксклюзивной очереди!"
    send_message(message)

