#!/bin/sh
set -e

echo "⏳ Ожидание PostgreSQL..."
until python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdshop.settings')
django.setup()
from django.db import connection
connection.ensure_connection()
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
