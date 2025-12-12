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
EXCHANGE_NAME = 'ikbo-27-22_contests_fanout'

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
    # Парсинг аргументов: сообщение и время сна
    # В PowerShell символ # является комментарием, поэтому передавайте время как число
    if len(sys.argv) < 2:
        print("Использование: python producer.py <сообщение> [время_сна]")
        print("Пример: python producer.py 'Сообщение для всех' 1")
        print("Примечание: В PowerShell используйте число без символа #")
        sys.exit(1)
    
    message = sys.argv[1]
    
    # Время сна можно передать как второй аргумент (число без символа #)
    if len(sys.argv) >= 3:
        try:
            sleep_time = int(sys.argv[2])
        except ValueError:
            # Если передан аргумент с # (для совместимости), попробуем извлечь число
            sleep_arg = sys.argv[2]
            if sleep_arg.startswith('#'):
                sleep_time = int(sleep_arg[1:])
            else:
                sleep_time = 1
    else:
        sleep_time = 1
    
    send_message(message, sleep_time)


