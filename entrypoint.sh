#!/bin/sh
set -e

echo "⏳ Ожидание PostgreSQL..."
until python -c "
import psycopg2, os
psycopg2.connect(
    dbname=os.environ['DB_NAME'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    host=os.environ['DB_HOST'],
    port=os.environ.get('DB_PORT', '5432'),
)
" 2>/dev/null; do
  sleep 1
done
echo "✅ PostgreSQL готов"

echo "🔄 Применяем миграции..."
python manage.py migrate --noinput

echo "📦 Собираем статику..."
python manage.py collectstatic --noinput

echo "🚀 Запускаем Gunicorn..."
exec gunicorn crowdshop.wsgi:application --config gunicorn.conf.py
