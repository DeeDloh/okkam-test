# 1. Используем заранее собранный базовый образ
FROM python:3.12-slim

# 2. Рабочая директория
WORKDIR /app

# 3. Лёгкие зависимости проекта (чаще меняются, не требуют C++)

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Хак для passlib (bcrypt bugfix)
# RUN sed -i 's/version = _bcrypt.__about__.__version__/version = _bcrypt.__version__/' /usr/local/lib/python3.12/site-packages/passlib/handlers/bcrypt.py

# 5. Копируем код проекта
COPY . .

# 6. Команда по умолчанию для запуска FastAPI через uvicorn
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

CMD ["sh", "start.sh"]