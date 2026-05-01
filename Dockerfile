FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости для сборки пакетов
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем poetry
RUN pip install poetry

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости без создания виртуального окружения
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

# Копируем исходный код
COPY . .