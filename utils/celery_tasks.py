# 文件名: Django_today -> celery_tasks
# 创建时间: 2020/6/21 16:48
from django.core.mail import send_mail
from django.conf import settings
from celery import Celery
import time, os
from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from django_redis import get_redis_connection
from django.template import loader, RequestContext
from Logging import Use_Loggin


# 在任务处理者一端加这几句
# import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_fresh.settings")
# django.setup()

# 创建一个Celery类的实例对象
app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/8')


# 定义任务函数
@app.task
def send_register_active_email(to_email, username, token):
    logging = Use_Loggin()
    subject = '天天生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = '<h1>%s, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/users/active/%s">http://127.0.0.1:8000/users/active/%s</a>' % (username, token, token)
    try:
        send_mail(subject, message, sender, receiver, html_message=html_message)
    except:
        logging("celery异步发送邮件失败")
    

# 生成首页静态页面
@app.task
def generate_static_index_html():
    logging = Use_Loggin()
    # 获取商品的种类信息
    types = GoodsType.objects.all()

    # 获取首页轮播商品信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')

    # 获取首页促销活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

    # 获取首页分类商品展示信息
    for type in types:  # GoodsType
        # 获取type种类首页分类商品的图片展示信息
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')

        # 获取type种类首页分类商品的文字展示信息
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

        # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
        type.image_banners = image_banners
        type.title_banners = title_banners


    # 组织模板上下文
    context = {'types': types,
               'goods_banners': goods_banners,
               'promotion_banners': promotion_banners}

    # 使用模板
    # 1.加载模板文件,返回模板对象
    temp = loader.get_template('static_index.html')

    # 2.模板渲染
    static_index_html = temp.render(context)

    # 生成首页对应静态文件
    save_path = os.path.join(settings.BASE_DIR, 'static/index_generate_static.html')
    with open(save_path, 'w') as f:
        f.write(static_index_html)
