"""
Задание 2.3: Producer с обменником типа topic
Символ для времени сна: -
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
EXCHANGE_NAME = 'inbo-04_laptev_topic'

def send_message(message, routing_key, sleep_time):
    """Отправка сообщения через topic обменник"""
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
        
        # Создание устойчивого обменника типа topic
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type='topic',
            durable=True  # Обменник сохраняется при перезапуске
        )
        
        # Отправка сообщения с routing_key (например: "stock.usa.usd" или "bond.russia.rub")
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Сообщение сохраняется на диск
            )
        )
        
        print(f" [x] Отправлено сообщение: {message}")
        print(f" [x] Routing key: {routing_key}")
        print(f" [x] Время сна: {sleep_time} секунд")
        
        time.sleep(sleep_time)
        
        connection.close()
        
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Использование: python producer.py <сообщение> <routing_key> -<время_сна>")
        print("Пример routing_key: stock.usa.usd или bond.russia.rub")
        sys.exit(1)
    
    message = sys.argv[1]
    routing_key = sys.argv[2]
    sleep_arg = sys.argv[3]
    
    if sleep_arg.startswith('-'):
        sleep_time = int(sleep_arg[1:])
    else:
        sleep_time = 1
    
    send_message(message, routing_key, sleep_time)


