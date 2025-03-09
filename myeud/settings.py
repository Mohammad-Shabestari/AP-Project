import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-رمز-تصادفی-خودتان-اینجا'
DEBUG = True

ALLOWED_HOSTS = ['*']  # برای تست روی لوکال

# اپ‌های نصب‌شده
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'corsheaders',
    'main_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # برای اجازه Cross-Origin
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myeud.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # مسیردهی برای تمپلیت مجزا و دلخواه
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

WSGI_APPLICATION = 'myeud.wsgi.application'
ASGI_APPLICATION = 'myeud.asgi.application'

# تنظیم پایگاه داده PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'unienroll_db',         # نام دیتابیس
        'USER': 'admin',             # کاربر دیتابیس
        'PASSWORD': 'Databasepos2025',       # رمز کاربر
        'HOST': 'localhost',            # یا آدرس سرور PG
        'PORT': '5432',                 # پورت پیشفرض PG
    }
}

# تنظیمات پسورد و کاربران
AUTH_PASSWORD_VALIDATORS = [
    # درصورت استفاده از سیستم User پیشفرض Django فعال می‌شود
    # جهت سادگی اینجا خالی گذاشته‌ایم.
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
TATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'main_app/static')
]

# تنظیمات CORS
CORS_ALLOW_ALL_ORIGINS = True


CRISPY_ALLOWED_TEMPLATE_PACKS = ("bootstrap5", "uni_form", "bootstrap4")
CRISPY_TEMPLATE_PACK = "bootstrap5"
