"""
Django settings for liuyingblog project.

Vue + DRF 架构：
- DRF 接管所有业务接口；管理后台由 admin-frontend (Vue) + adminapi (DRF) 完全承接
- simplejwt 提供 JWT 认证
- corsheaders 放行 Vite 开发服务器
- Django Admin / Jazzmin / sessions / messages / staticfiles 已全部移除
- 模板系统仅保留邮箱验证码邮件渲染所需
"""
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# 加载根目录的 .env 文件
load_dotenv(os.path.join(BASE_DIR, '.env'))


# ==========================================
# 基础配置
# ==========================================
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'fallback-secret-key-for-local-dev')
DEBUG = os.getenv('DJANGO_DEBUG') == 'True'
ALLOWED_HOSTS = ['43.163.232.238', 'www.liuying.com', 'liuying.com', '127.0.0.1', 'localhost']


# ==========================================
# Application definition
# ==========================================
INSTALLED_APPS = [
    # Django 必要组件（auth/contenttypes 提供 User 模型与外键，迁移不可缺）
    'django.contrib.auth',
    'django.contrib.contenttypes',

    # 第三方
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',

    # 业务
    'blog',
    'liuyingauth',
    'adminapi',
]

MIDDLEWARE = [
    # corsheaders 必须放在 CommonMiddleware 之前
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'liuyingblog.urls'

# 仅用于 render_to_string 渲染邮箱验证码邮件正文（liuyingauth/templates/...）
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'liuyingblog.wsgi.application'


# ==========================================
# Database
# ==========================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==========================================
# i18n
# ==========================================
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = False


# ==========================================
# 媒体文件
# 前端构建产物由 Nginx 直接托管；Django 已不再提供 admin 自身静态资源
# ==========================================
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==========================================
# 邮件配置
# ==========================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = '3302393536@qq.com'
EMAIL_FROM_NAME = '流萤博客'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = '3302393536@qq.com'

DJANGO_MYSQL_VERSION_CHECK = False


# ==========================================
# DRF + JWT
# ==========================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# ==========================================
# CORS（开发环境放行两个 Vite 前端）
# ==========================================
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',   # frontend  用户前台
    'http://127.0.0.1:5173',
    'http://localhost:5174',   # admin-frontend  管理后台
    'http://127.0.0.1:5174',
]
CORS_ALLOW_CREDENTIALS = True


# ==========================================
# 自定义认证后端：邮箱/用户名都可登录
# ==========================================
AUTHENTICATION_BACKENDS = [
    'liuyingauth.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]


# ==========================================
# Redis 缓存
# 本机 Redis：端口 6379，1 号库与其他应用隔离
# 如果你的 Redis 配了密码，把它放进 .env：REDIS_PASSWORD=xxx
# 也可以直接用 REDIS_URL=redis://:password@127.0.0.1:6379/1 一把覆盖
# ==========================================
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
if os.getenv('REDIS_URL'):
    REDIS_URL = os.getenv('REDIS_URL')
elif REDIS_PASSWORD:
    REDIS_URL = f'redis://:{REDIS_PASSWORD}@127.0.0.1:6379/1'
else:
    REDIS_URL = 'redis://127.0.0.1:6379/1'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
}
