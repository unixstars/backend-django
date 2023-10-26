"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.2.

settings.py 추가정보
https://docs.djangoproject.com/en/4.2/topics/settings/

settings.py 모든정보
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta
from corsheaders.defaults import default_headers

# .env 파일 로드
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 환경에 따른 분리
ENV_ROLE = os.getenv("ENV_ROLE")
dev = "development"
prod = "production"

# 프로덕트 전 체크리스트
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: 프로덕트 환경에서는 반드시 False로!
if ENV_ROLE == dev:
    DEBUG = True
elif ENV_ROLE == prod:
    DEBUG = False

if ENV_ROLE == dev:
    ALLOWED_HOSTS = [
        ".ap-northeast-2.compute.amazonaws.com",
        "unistar-backend-dev.com",
        "172.31.41.0",
        "127.0.0.1",
    ]
elif ENV_ROLE == prod:
    ALLOWED_HOSTS = [
        ".ap-northeast-2.compute.amazonaws.com",
        "company.getunivxstartnow.com",
        "unistar-backend.com",
    ]


# Application 정의
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # CORS
    "corsheaders",
    # AWS S3
    "storages",
    # django-rest-auth
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt.token_blacklist",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    # django-allauth
    "allauth",
    "allauth.account",
    # apps
    "api.apps.ApiConfig",
    "activity.apps.ActivityConfig",
    "user.apps.UserConfig",
    "program.apps.ProgramConfig",
    "authentication.apps.AuthenticationConfig",
    # crontab(작업 자동화)
    "django_crontab",
]

# 커스텀 유저 모델
AUTH_USER_MODEL = "user.User"

# 로그인 시 인증 방법(장고는 리스트의 모든 인증을 시도)
AUTHENTICATION_BACKENDS = {
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
}

# SITE_ID : auth 시 기본 id 필요
# 여러 App/웹사이트에서 하나의 백엔드 사용 시 SITE 분리
SITE_ID = 1

MIDDLEWARE = [
    # CORS 미들웨어
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# CORS 설정
if ENV_ROLE == dev:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
    ]
elif ENV_ROLE == prod:
    CORS_ALLOWED_ORIGINS = [
        "https://company.getunivxstartnow.com",
    ]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    *default_headers,
    "access-control-allow-credentials",
]

# REST_FRAMEWORK 설정
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    # Throttling(API 횟수 제한)
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "2000/day",
        "user": "1000/day",
        "dj_rest_auth": "200/day",
        "custom": "100/day",
    },
}

# 반복작업
CRONJOBS = [
    (
        "0 0 * * *",
        "authentication.cron.delete_expired_tokens",
        "> /var/log/uwsgi/cron/delete_expired_tokens.log",
    ),
    (
        "*/60 * * * *",
        "activity.cron.close_expired_boards",
        "> /var/log/uwsgi/cron/close_update.log",
    ),
    (
        "0 0 * * *",
        "program.cron.update_accepted_applicants",
        "> /var/log/uwsgi/cron/update_accepted_applicants.log",
    ),
]


# Email 로그인 관련(dj-rest-auth 설정)
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "none"

# 콘솔 출력(전송)용 이메일 백엔드(개발 및 테스트용)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# JWT 토큰 사용(dj-rest-auth)
REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_SECURE": True,
    "JWT_AUTH_HTTPONLY": False,
    "SESSION_LOGIN": False,
}

# JWT Token 설정(simple JWT)
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=6),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
}

CSRF_COOKIE_SECURE = True

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# 데이터베이스
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

"""
# 장고 로컬 db
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
"""

if ENV_ROLE == dev:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DB_NAME_DEV"),
            "USER": os.getenv("DB_USER_DEV"),
            "PASSWORD": os.getenv("DB_PASSWORD_DEV"),
            "HOST": os.getenv("DB_HOST_DEV"),
            "PORT": "3306",
            "OPTIONS": {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        },
    }
elif ENV_ROLE == prod:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST"),
            "PORT": "3306",
            "OPTIONS": {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        },
    }


# 비밀번호 validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# 다국적 언어 설정
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = False

# Static 파일들 (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

"""
# 로컬 환경 Static, Media 설정
STATIC_URL = "/static/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
"""

# 기본 primary key field 타입
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# AWS Access 설정
if ENV_ROLE == dev:
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME_DEV")
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
elif ENV_ROLE == prod:
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}


# Static 파일 설정
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")


# Media 파일 설정
MEDIA_LOCATION = "media"
DEFAULT_FILE_STORAGE = "mystorages.MediaStorage"
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{MEDIA_LOCATION}/"

# 파일 업로드 크기 제한(한 번의 요청)
DATA_UPLOAD_MAX_MEMORY_SIZE = 54 * 1024 * 1024  # 54 MB
