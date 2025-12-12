FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Serverless Containers в Яндекс.Облаке устанавливают PORT автоматически
# По умолчанию это 8080, но может быть любое значение
# Не устанавливаем PORT здесь, чтобы использовать значение из окружения

# Используем gunicorn для production
# PORT будет установлен Яндекс.Облаком автоматически (обычно 8080)
# Используем sh для правильной подстановки переменной окружения
CMD sh -c 'gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 2 --timeout 30 --access-logfile - --error-logfile - app:app'


