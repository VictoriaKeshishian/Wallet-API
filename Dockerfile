# Указываем базовый образ
FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y postgresql-client


# Копируем все остальные файлы проекта
COPY . .

# Указываем переменные окружения
ENV DATABASE_URL=postgres://user:password1@db:5432/wallet_db

# Запускаем приложение с правильным путем к main.py
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
