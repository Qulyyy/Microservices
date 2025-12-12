"""
Задание 2.3: Consumer с обменником типа topic
Символ для времени сна: -
Поддерживает паттерны в routing_key: * (одно слово), # (любое количество слов)
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
EXCHANGE_NAME = 'ikbo-27-22_contests_topic'

def callback(ch, method, properties, body, sleep_time):
    """Обработка полученного сообщения"""
    print(f" [x] Получено сообщение: {body.decode()}")
    print(f" [x] Routing key: {method.routing_key}")
    print(f" [x] Обработка займет {sleep_time} секунд")
    time.sleep(sleep_time)
    print(" [x] Сообщение обработано")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def consume_messages(binding_key, sleep_time):
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
        
        # Создание устойчивого обменника типа topic
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type='topic',
            durable=True
        )
        
        # Создание очереди
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        
        # Связывание очереди с обменником по binding_key
        # binding_key может содержать паттерны: * (одно слово), # (любое количество слов)
        # Примеры: "stock.*.usd", "*.usa.*", "#.russia.#"
        channel.queue_bind(
            exchange=EXCHANGE_NAME,
            queue=queue_name,
            routing_key=binding_key
        )
        
        def callback_wrapper(ch, method, properties, body):
            callback(ch, method, properties, body, sleep_time)
        
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback_wrapper
        )
        
        print(f' [*] Ожидание сообщений с binding_key="{binding_key}". Время обработки: {sleep_time} сек.')
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
        print("Использование: python consumer.py <binding_key> [время_сна]")
        print("Пример: python consumer.py 'stock.*.usd' 1")
        print("Примеры binding_key:")
        print("  stock.*.usd  - все акции в долларах")
        print("  *.usa.*      - все активы на рынке США")
        print("  #.russia.#   - все активы, связанные с Россией")
        print("Примечание: В PowerShell используйте число без символа -")
        sys.exit(1)
    
    binding_key = sys.argv[1]
    
    # Время сна опционально
    if len(sys.argv) >= 3:
        sleep_arg = sys.argv[2]
        if sleep_arg.startswith('-'):
            sleep_time = int(sleep_arg[1:])
        else:
            try:
                sleep_time = int(sleep_arg)
            except ValueError:
                sleep_time = 1
    else:
        sleep_time = 1
    
    consume_messages(binding_key, sleep_time)


