# 文件名: Django_today -> celery_tasks
# 创建时间: 2020/6/21 16:48

# 使用celery
from django.core.mail import send_mail
from django.conf import settings
from celery import Celery
import time

# 在任务处理者一端加这几句
# import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
# django.setup()

# 创建一个Celery类的实例对象
app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/8')


# 定义任务函数
@app.task
def send_register_active_email(to_email, username, token):
    subject = '天天生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = '<h1>%s, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/users/active/%s">http://127.0.0.1:8000/users/active/%s</a>' % (username, token, token)
    try:
        send_mail(subject, message, sender, receiver, html_message=html_message)
    except:
        print("error")
    # time.sleep(5)