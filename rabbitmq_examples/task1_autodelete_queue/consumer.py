"""
Задание 1.3: Consumer для автоудаляемой очереди
"""
import pika
import time

# Параметры подключения
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'guest'
RABBITMQ_PASSWORD = 'guest'

# Название очереди
QUEUE_NAME = 'ikbo-27-22_contests_autodelete'

def callback(ch, method, properties, body):
    """Обработка полученного сообщения"""
    print(f" [x] Получено сообщение: {body.decode()}")
    time.sleep(1)
    print(" [x] Сообщение обработано")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def consume_messages():
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
        
        # Создание автоудаляемой очереди
        channel.queue_declare(queue=QUEUE_NAME, auto_delete=True)
        
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback
        )
        
        print(' [*] Ожидание сообщений. Для выхода нажмите CTRL+C')
        print(' [*] Очередь будет удалена при отключении этого потребителя')
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print('\n [*] Остановка получения сообщений')
        channel.stop_consuming()
        connection.close()
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == '__main__':
    consume_messages()


