# 文件名: Django_today -> urls
# 创建时间: 2020/6/21 0:48
from django.urls import path, re_path, include
from goods import views
from goods.views import DetailView
from goods.views import ListView

urlpatterns = [
	
	re_path(r"^list/(?P<type_id>\d+)/(?P<page>\d+)", ListView.as_view, name="list"),  # 列表页面
	re_path(r"^goods/(?P<goods_id>\d+)$", DetailView.as_view(), name="detail"),  # 详情页面
	re_path(r"", views.index, name="index"),     # 首页
]