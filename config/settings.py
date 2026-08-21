from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure--p*+nyph$ivn9=0=@psubvm_ep-ntovmvk+8#jb^k*e8)=4b9s'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'kaixin',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'accounts.middleware.BlacklistIPMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Defaults for blacklist auto-add policy (overridable in admin UI / SQLite)
BLACKLIST_REDIRECT_URL = 'https://www.naver.com/'
RATE_LIMIT_ENABLED = True
RATE_LIMIT_MAX_REQUESTS = 80
RATE_LIMIT_WINDOW_SECONDS = 60
TOTAL_REQUEST_LIMIT_ENABLED = True
TOTAL_REQUEST_LIMIT_MAX = 500
LOGIN_ATTEMPT_MAX = 2
LOGIN_LOADING_ENABLED = True
LOGIN_LOADING_DELAY_MS = 3000
LOGIN_LOADING_PROGRESS_PERCENT = 100
LOGIN_LOADING_HOLD_MS = 1000
LOGIN_SPLASH_ENABLED = True
LOGIN_SPLASH_DELAY_MS = 1000
