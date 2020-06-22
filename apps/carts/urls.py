# 文件名: Django_today -> urls
# 创建时间: 2020/6/21 0:48
from django.contrib import admin
from django.urls import path, re_path, include
from carts import views


urlpatterns = [
		re_path(r"demo", views.createsession),
]