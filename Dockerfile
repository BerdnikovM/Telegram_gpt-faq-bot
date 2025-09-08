FROM python:3.12-slim

WORKDIR /app

# Установка зависимостей проекта
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Запускаем бота
CMD ["python", "-m", "app.bot"]
