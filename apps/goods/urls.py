# 文件名: Django_today -> urls
# 创建时间: 2020/6/21 0:48
from django.urls import path, re_path, include
from goods import views


urlpatterns = [
	re_path(r"", views.index, name="index"),  # 首页
]