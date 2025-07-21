import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

VALID_API_KEYS = env("VALID_API_KEYS").split(",")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

PROJECT_APPS = [
    'apps.blog'
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'channels',
    'django_ckeditor_5',
    'django_celery_results',
    'django_celery_beat',
    'rest_framework_api', #para respuesta standar
    'storages',
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + THIRD_PARTY_APPS

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "undo",
            "redo",
            "|",
            "heading",
            "|",
            "bold",
            "italic",
            "underline",
            "link",
            "|",
            "code",
            "codeBlock",
            "blockQuote",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "insertTable",
            "imageUpload",
            "mediaEmbed",
            "|",
            "outdent",
            "indent",
            "|",
            "removeFormat",
            "horizontalLine",
        ],
        "autoParagraph": False
    }
}
CKEDITOR_5_CUSTOM_CSS = "custom/ckeditor_fix.css"


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

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

print("DB HOST:--------------------------- ", env("DATABASE_HOST"))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("DATABASE_NAME"),
        'USER': env("DATABASE_USER"),
        'PASSWORD': env("DATABASE_PASSWORD"),
        'HOST': env("DATABASE_HOST"),
        'PORT': 5432
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

#Comentado cuando se definio AWS
#STATIC_LOCATION = "static"
#STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "staticfiles")] #
#STATIC_ROOT = os.path.join(BASE_DIR, "static")
#MEDIA_URL = 'media/'
#MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#DEFINE QIUEN PUEDE USAR LA API
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny" #se cambio "rest_framework.permissions.IsAuthenticatedOrReadOnly" si esta autenticado puede usarlo, de lo contrario solo leer
    ],
}

CHANNELLS_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "host": [env("REDIS_URL")]
        }
    }
}

REDIS_HOST = env("REDIS_HOST")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        }
    }
}

CHANNELS_ALLOWED_ORIGINS = "http://localhost:3000"

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Santiago"

CELERY_BROKER_URL = env("REDIS_URL")
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 3600,
    'socket_timeout': 5,
    'retry_on_timeout': True
}

CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'

CELERY_IMPORTS = (
    'core.tasks',
    'apps.blog.tasks'
)

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {}

# Configuraciones de AWS
AWS_ACCESS_KEY_ID=env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY=env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME=env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME=env("AWS_S3_REGION_NAME")
AWS_S3_CUSTOM_DOMAIN=f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"

#Configuracion de almacenamiento predeterminado
#DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage" se cambio por el de abajo 

# Configuración de seguridad y permisos
AWS_QUERYSTRING_AUTH = False # Deshabilita las firmas en las URLs (archivos públicos)
AWS_FILE_OVERWRITE = False # Evita sobrescribir archivos con el mismo nombre
AWS_DEFAULT_ACL = None # Define el control de acceso predeterminado como público
AWS_QUERYSTRING_EXPIRE = 5 # Tiempo de expiración de las URLs firmadas

# Parámetros adicionales para los objetos de S3
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400" # Habilita el almacenamiento en caché por un día
}

# Configuración de archivos estáticos
STATIC_LOCATION = "static"
STATIC_URL = f"{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/"
STATICFILES_STORAGE = "core.storage_backends.StaticStorage"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Configuración de archivos de medios
MEDIA_LOCATION = "media"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/"
MEDIA_ROOT = MEDIA_URL
DEFAULT_FILE_STORAGE = "core.storage_backends.PublicMediaStorage"