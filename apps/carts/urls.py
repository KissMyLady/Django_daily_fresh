# 文件名: Django_today -> urls
# 创建时间: 2020/6/21 0:48
from django.contrib import admin
from django.urls import path, re_path, include
from carts import views
from carts.views import CartInfoShow
from carts.views import UpdataAjax
from carts.views import DeleteAjax

urlpatterns = [
		# 异步删除
		re_path(r"delete", DeleteAjax.as_view(), name="delete"),
	
		# 购物车异步刷新点击加减的数量
		re_path(r"update", UpdataAjax.as_view(), name="update"),
		
		# 购物车添加商品接口
		re_path(r"^add$",  views.addCart, name="add"),
	
		# 测试界面
		re_path(r"demo",   views.createsession),
	
		# 购物车界面显示 /carts/
		re_path(r'', CartInfoShow.as_view(), name='cart'),
]