# 🛒 КраудШоп — Платформа совместных покупок

MVP веб-приложение для организации групповых закупок (crowd-shopping).

## 📋 Технологии

- **Python 3.11** + **Django 4.2** + **DRF 3.14**
- **Gunicorn 21** (WSGI-сервер)
- **Nginx 1.25** (reverse proxy, раздача статики)
- **PostgreSQL 15** (в Docker)
- **Bootstrap 5.3** (адаптивный русский интерфейс)
- **Docker + docker-compose** (3 контейнера)

---

## 🏗 Архитектура

```
Браузер
   │  :80
   ▼
┌──────────┐   /static/   ┌──────────────┐
│  Nginx   │──────────────▶  staticfiles  │ (volume)
│ (proxy)  │   /media/    └──────────────┘
└────┬─────┘
     │ proxy_pass :8000
     ▼
┌──────────┐
│ Gunicorn │  (workers = CPU×2+1)
│  Django  │
└────┬─────┘
     │
     ▼
┌──────────┐
│ Postgres │
└──────────┘
```

---

## 🚀 Быстрый старт

```bash
# 1. Распакуйте архив
unzip crowdshop.zip && cd crowdshop

# 2. Запустите все сервисы
docker-compose up --build -d

# 3. Загрузите начальные данные
docker-compose exec web python manage.py loaddata purchases/fixtures/categories.json
docker-compose exec web python manage.py create_demo_data
```

### Откройте в браузере

| Адрес | Описание |
|-------|----------|
| http://localhost | Сайт (через Nginx) |
| http://localhost/admin | Административная панель |
| http://localhost/api/v1/ | REST API |

---

## 👥 Тестовые аккаунты

| Логин        | Пароль     | Роль              |
|-------------|------------|-------------------|
| `admin`     | `admin123` | Суперпользователь |
| `organizer` | `demo123`  | Организатор       |
| `buyer`     | `demo123`  | Покупатель        |

---

## 📁 Структура проекта

```
crowdshop/
├── nginx/
│   ├── nginx.conf        # Основной конфиг nginx
│   └── default.conf      # Конфиг сайта (upstream, static, proxy)
├── crowdshop/            # Django-пакет
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                # Приложение пользователей
├── purchases/            # Основное приложение
├── api/                  # REST API (DRF)
├── templates/            # HTML-шаблоны
├── static/               # Исходная статика
├── gunicorn.conf.py      # Конфиг Gunicorn
├── entrypoint.sh         # Скрипт запуска (migrate → collectstatic → gunicorn)
├── Dockerfile
├── docker-compose.yml    # web + db + nginx
└── requirements.txt
```

---

## 🔌 REST API

Базовый URL: `http://localhost/api/v1/`

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/v1/purchases/` | Список закупок |
| POST | `/api/v1/purchases/` | Создать закупку |
| GET | `/api/v1/purchases/{id}/` | Детали закупки |
| GET | `/api/v1/purchases/{id}/orders/` | Заявки закупки |
| GET | `/api/v1/categories/` | Список категорий |
| GET | `/api/v1/orders/` | Мои заявки |
| POST | `/api/v1/orders/{id}/cancel/` | Отменить заявку |

### Фильтры

```
?search=куртка          # полнотекстовый поиск
?category=clothing      # slug категории
?status=collecting      # статус закупки
?ordering=-price_per_unit
```

---

## 🔄 Команды Docker

```bash
# Запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f nginx
docker-compose logs -f web

# Пересборка после изменений кода
docker-compose up --build -d

# Остановка
docker-compose down

# Полный сброс (включая данные БД)
docker-compose down -v

# Shell в контейнере Django
docker-compose exec web bash

# Django management commands
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell
```

---

## ⚙️ Переменные окружения (.env)

```env
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=False          # В продакшене обязательно False
ALLOWED_HOSTS=localhost,yourdomain.com

DB_NAME=crowdshop
DB_USER=crowdshop_user
DB_PASSWORD=crowdshop_pass
DB_HOST=db
DB_PORT=5432
```
