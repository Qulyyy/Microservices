"""
Задание 2.1: Consumer с обменником типа fanout
Символ для времени сна: #
"""
import pika
import time
import sys

# Параметры подключения
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'guest'
RABBITMQ_PASSWORD = 'guest'

# Название обменника
EXCHANGE_NAME = 'inbo-04_laptev_fanout'

def callback(ch, method, properties, body, sleep_time):
    """Обработка полученного сообщения"""
    print(f" [x] Получено сообщение: {body.decode()}")
    print(f" [x] Обработка займет {sleep_time} секунд")
    time.sleep(sleep_time)
    print(" [x] Сообщение обработано")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def consume_messages(sleep_time):
    """Получение сообщений из очереди"""
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
            durable=True
        )
        
        # Создание временной очереди (удаляется при отключении потребителя)
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        
        # Связывание очереди с обменником
        # В fanout routing_key не используется
        channel.queue_bind(
            exchange=EXCHANGE_NAME,
            queue=queue_name
        )
        
        # Создание callback с параметром времени сна
        def callback_wrapper(ch, method, properties, body):
            callback(ch, method, properties, body, sleep_time)
        
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback_wrapper
        )
        
        print(f' [*] Ожидание сообщений. Время обработки: {sleep_time} сек. Для выхода нажмите CTRL+C')
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print('\n [*] Остановка получения сообщений')
        channel.stop_consuming()
        connection.close()
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == '__main__':
    # Парсинг времени сна из аргументов
    if len(sys.argv) > 1 and sys.argv[1].startswith('#'):
        sleep_time = int(sys.argv[1][1:])
    else:
        sleep_time = 1
    
    consume_messages(sleep_time)


