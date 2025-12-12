FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Используем PORT из переменных окружения (для Serverless Containers)
# По умолчанию 5002 для локальной разработки
ENV PORT=5002

EXPOSE 5002

# Используем gunicorn для production
# Для Serverless Containers Яндекс.Облако автоматически устанавливает PORT
# Используем sh для правильной подстановки переменной окружения
CMD sh -c 'gunicorn --bind 0.0.0.0:${PORT:-5002} --workers 1 --threads 2 --timeout 30 --access-logfile - --error-logfile - app:app'


