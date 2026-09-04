#!/bin/sh
set -e

echo "Ожидание PostgreSQL..."
while ! nc -z db 5432; do
  echo "   База ещё не готова, ждём..."
  sleep 1
done

echo "PostgreSQL готов!"

echo "Применяем Alembic миграции..."
alembic upgrade head

echo "Запуск приложения..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000