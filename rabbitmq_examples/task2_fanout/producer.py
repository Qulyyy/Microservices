"""
Задание 2.1: Producer с обменником типа fanout
Символ для времени сна: #
Сообщения должны храниться при выключении RabbitMQ
"""
import pika
import sys
import time

# Параметры подключения
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'guest'
RABBITMQ_PASSWORD = 'guest'

# Название обменника
EXCHANGE_NAME = 'inbo-04_laptev_fanout'

def send_message(message, sleep_time):
    """Отправка сообщения через fanout обменник"""
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
        
        # Создание устойчивого обменника типа fanout
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type='fanout',
            durable=True  # Обменник сохраняется при перезапуске
        )
        
        # Отправка сообщения
        # В fanout routing_key игнорируется, сообщение отправляется во все связанные очереди
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key='',  # В fanout routing_key не используется
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Сообщение сохраняется на диск
            )
        )
        
        print(f" [x] Отправлено сообщение: {message}")
        print(f" [x] Время сна: {sleep_time} секунд")
        
        # Сон перед отправкой следующего сообщения
        time.sleep(sleep_time)
        
        connection.close()
        
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

if __name__ == '__main__':
    # Парсинг аргументов: сообщение и время сна (символ #)
    if len(sys.argv) < 3:
        print("Использование: python producer.py <сообщение> #<время_сна>")
        sys.exit(1)
    
    message = sys.argv[1]
    sleep_arg = sys.argv[2]
    
    if sleep_arg.startswith('#'):
        sleep_time = int(sleep_arg[1:])
    else:
        sleep_time = 1
    
    send_message(message, sleep_time)


