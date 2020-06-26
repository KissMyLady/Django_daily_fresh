import os, sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'lqn!i8wnk07hb$jaww)93yl&%(d-8h8mcts7(+6j4(&rza)s$c'
DEBUG = True
ALLOWED_HOSTS = ["*"]

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

# 首页缓存时间 单位:秒
INDEX_CASH_CACHE_EXPIRE = 3600


sys.path.insert(1, os.path.join(BASE_DIR, 'libs'))
sys.path.insert(2, os.path.join(BASE_DIR, 'utils'))
from utils import Logging
from utils import updown_image  # 图片上传 云平台

sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'carts', 'goods', 'orders', 'users',  # 4个App注册
    'tinymce',   # 注册富文本编辑器, 然后在下面设置内容
    'haystack',  # 启用全文检索框架
]


# 副文本编辑器配置  这里只在后台管理用
TINYMCE_DEFAULT_CONFIG = {
    # 'theme': 'advacnced',  # 主题 高级
    'theme': 'mobile',
    'width': 600,
    'height': 400,
    'language': 'zh_CN',
     'plugins': [
            'powerpaste table advlist autolink lists link charmap print preview hr anchor pagebreak',
            'searchreplace wordcount visualblocks visualchars code fullscreen',
            'insertdatetime nonbreaking save table contextmenu directionality',
            'emoticons textcolor colorpicker textpattern image code codesample toc pagebreak'],
    'toolbar1': 'undo redo | table | insert | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
    'toolbar2': 'print preview | forecolor backcolor emoticons | codesample | pagebreak | toc | fullscreen',

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
          "LOCATION": "redis://127.0.0.1:6379/0",
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


# 配置搜索引擎
HAYSTACK_CONNECTIONS = {
    'default': {
        # 使用whoosh引擎 py path: /lib/package/
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        # 索引文件路径 设置生成的索引文件的路径(文件)
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    }
}

# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'