"""
Задание 2.2: Consumer с обменником типа direct
Символ для времени сна: *
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
EXCHANGE_NAME = 'ikbo-27-22_contests_direct'

def callback(ch, method, properties, body, sleep_time):
    """Обработка полученного сообщения"""
    print(f" [x] Получено сообщение: {body.decode()}")
    print(f" [x] Routing key: {method.routing_key}")
    print(f" [x] Обработка займет {sleep_time} секунд")
    time.sleep(sleep_time)
    print(" [x] Сообщение обработано")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def consume_messages(routing_key, sleep_time):
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
        
        # Создание обменника типа direct
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type='direct',
            durable=False
        )
        
        # Создание очереди
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        
        # Связывание очереди с обменником по routing_key
        channel.queue_bind(
            exchange=EXCHANGE_NAME,
            queue=queue_name,
            routing_key=routing_key
        )
        
        def callback_wrapper(ch, method, properties, body):
            callback(ch, method, properties, body, sleep_time)
        
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback_wrapper
        )
        
        print(f' [*] Ожидание сообщений с routing_key="{routing_key}". Время обработки: {sleep_time} сек.')
        print(' [*] Для выхода нажмите CTRL+C')
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print('\n [*] Остановка получения сообщений')
        channel.stop_consuming()
        connection.close()
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python consumer.py <routing_key> [время_сна]")
        print("Пример: python consumer.py info 1")
        print("Примечание: В PowerShell используйте число без символа *")
        sys.exit(1)
    
    routing_key = sys.argv[1]
    
    # Время сна опционально
    if len(sys.argv) >= 3:
        sleep_arg = sys.argv[2]
        if sleep_arg.startswith('*'):
            sleep_time = int(sleep_arg[1:])
        else:
            try:
                sleep_time = int(sleep_arg)
            except ValueError:
                sleep_time = 1
    else:
        sleep_time = 1
    
    consume_messages(routing_key, sleep_time)


