FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY static/ static/

# Для Serverless Containers Яндекс.Облако устанавливает PORT автоматически (обычно 8080)
# PORT - зарезервированная переменная, нельзя устанавливать явно
# По умолчанию используем 8080 для Serverless Containers
# Для локальной разработки docker-compose установит PORT=5002
ENV PORT=8080

EXPOSE 8080

# Используем gunicorn для production
# PORT будет установлен из переменной окружения:
# - 8080 по умолчанию (для Serverless Containers)
# - 5002 для локальной разработки (docker-compose установит PORT=5002)
CMD sh -c 'gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 2 --timeout 30 --access-logfile - --error-logfile - app:app'


