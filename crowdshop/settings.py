import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-12345')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']  # Railway домен добавится автоматически

RAILWAY_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'crispy_forms',
    'crispy_bootstrap5',
    'users',
    'purchases',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crowdshop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'crowdshop.wsgi.application'

# ── База данных ────────────────────────────────────────────────────────────
# Пробуем DATABASE_URL (Railway), потом отдельные PG* (Railway альтернатива),
# потом DB_* (Docker Compose .env).

_database_url = os.environ.get('DATABASE_URL', '')

if _database_url:
    import dj_database_url
    DATABASES = {'default': dj_database_url.parse(_database_url, conn_max_age=600)}
else:
    # Собираем из отдельных переменных — Railway или Docker Compose
    _db_host = os.environ.get('DB_HOST')
    if _db_host == 'db' and os.environ.get('RAILWAY_ENVIRONMENT'):
        # DB_HOST=db — дефолт Docker Compose, на Railway не работает
        _db_host = None

    _host = os.environ.get('PGHOST') or _db_host
    if not _host:
        _host = 'db' if not os.environ.get('RAILWAY_ENVIRONMENT') else None

    if not _host:
        raise ImproperlyConfigured(
            'На Railway нужна переменная DATABASE_URL. '
            'Добавьте PostgreSQL в проект и привяжите его к сервису '
            '(Variables → Add Reference → DATABASE_URL). '
            'Удалите DB_HOST=db из переменных окружения.'
        )
    _port = (
        os.environ.get('PGPORT') or
        os.environ.get('DB_PORT') or
        '5432'
    )
    _name = (
        os.environ.get('PGDATABASE') or
        os.environ.get('DB_NAME') or
        'crowdshop'
    )
    _user = (
        os.environ.get('PGUSER') or
        os.environ.get('DB_USER') or
        'crowdshop_user'
    )
    _password = (
        os.environ.get('PGPASSWORD') or
        os.environ.get('DB_PASSWORD') or
        'crowdshop_pass'
    )

    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql',
            'NAME':     _name,
            'USER':     _user,
            'PASSWORD': _password,
            'HOST':     _host,
            'PORT':     _port,
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
_static_dir = BASE_DIR / 'static'
STATICFILES_DIRS = [_static_dir] if os.path.isdir(_static_dir) else []
#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
#STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

CSRF_TRUSTED_ORIGINS = ['https://*.railway.app']
if RAILWAY_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RAILWAY_DOMAIN}')
