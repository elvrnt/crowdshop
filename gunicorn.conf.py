# gunicorn.conf.py
import multiprocessing

# Сокет / адрес
bind = "0.0.0.0:8000"

# Количество воркеров: 2 * CPU + 1 — стандартная рекомендация
workers = multiprocessing.cpu_count() * 2 + 1

# Тип воркера
worker_class = "sync"

# Таймауты
timeout = 120
keepalive = 5

# Логирование
accesslog = "-"   # stdout
errorlog = "-"    # stderr
loglevel = "info"

# Перезапуск воркеров после N запросов (защита от утечек памяти)
max_requests = 1000
max_requests_jitter = 100

# Предзагрузка приложения (экономит память через copy-on-write)
preload_app = True
