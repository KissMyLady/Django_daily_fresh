import os, sys

# 邮箱激活有效时间 单位:秒
EMAIL_ACITVATE_EXPIRE = 3600

# 登录 Cookie记住记住用户名时间 单位:秒
LOGIN_COOKIE_EXPIRE = 7 * 24 * 3600

# 当用户未登录时, 被重定向到的url地址
LOGIN_URL = "/user/login"

# 云平台储存图片url前缀
CLOUDY_IMG_URL_PREFIX = 'http://qbg25zlw0.bkt.clouddn.com/'

# 设置Django的文件存储类-自定义储存类型
DEFAULT_FILE_STORAGE='utils.DFS.storage.FDFSStorage'


# -------------------------------------------------------------------
# -------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'lqn!i8wnk07hb$jaww)93yl&%(d-8h8mcts7(+6j4(&rza)s$c'
DEBUG = True
ALLOWED_HOSTS = ["*"]

sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'carts', 'goods', 'orders', 'users',
    'tinymce',  # 注册富文本编辑器, 然后在下面设置内容
    'haystack',
]

# 副文本编辑器配置  这里只在后台管理用
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advacnced',  # 主题 高级
    'width': 600,
    'height': 400,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'my_fresh.urls'
AUTH_USER_MODEL = 'users.User'
SILENCED_SYSTEM_CHECKS = ['fields.E300', 'fields.E307']


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# 静态文件添加
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),  # 注意括号后面的还有个逗号
)

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')

sys.path.insert(1, os.path.join(BASE_DIR, 'libs'))
sys.path.insert(1, os.path.join(BASE_DIR, 'utils'))

# 导入自建模块
from utils import Logging
from utils import celery_tasks
from utils import updown_image  # 图片上传 云平台


WSGI_APPLICATION = 'my_fresh.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'daily_sql',
        'USER': 'root',
        'PASSWORD': 'YING123ZZ',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

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

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/



# ROOT_URLCONF = 'daily_fresh.urls'

# 设置reids作为缓存
CACHES = {
    "default": {
         "BACKEND": "django_redis.cache.RedisCache",
          "LOCATION": "redis://127.0.0.1:6379/3",
          "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    "CONNECTION_POOL_KWARGS": {"max_connections": 100}
          },
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIADS = "default"
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend']


# 发送邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'kiss_mylady@qq.com'
EMAIL_HOST_PASSWORD = 'sgngqtmfnkmpfega'  # 通过邮箱发送短信获取
EMAIL_FROM = '基地工程<kiss_mylady@qq.com>'