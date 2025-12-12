FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Для локальной разработки используем порт 5002
# Для Serverless Containers Яндекс.Облако установит PORT автоматически (обычно 8080)
ENV PORT=5002

EXPOSE 5002

# Используем gunicorn для production
# PORT будет установлен из переменной окружения:
# - 5002 для локальной разработки (docker-compose)
# - 8080 для Serverless Containers (устанавливается Яндекс.Облаком)
CMD sh -c 'gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 2 --timeout 30 --access-logfile - --error-logfile - app:app'


