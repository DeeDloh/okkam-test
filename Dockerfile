# 1. Используем заранее собранный базовый образ
FROM python:3.12-slim

# 2. Рабочая директория
WORKDIR /app

# psql нужен start.sh для загрузки CSV в базу
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

CMD ["sh", "start.sh"]
