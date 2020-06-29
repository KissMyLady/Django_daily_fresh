# 文件名: Django_today -> urls
# 创建时间: 2020/6/21 0:48
from django.urls import path, re_path, include
from orders.views import OrderPlaceInfo
from orders.views import OredrCommit_badlock
from orders.views import OrderPayView
from orders.views import CheckPay
from orders.views import Comment


urlpatterns = [
	# 评价
	re_path(r"comment/(?P<order_id>.+)$", Comment.as_view(), name="comment"),
	
	# 支付后, 状态查询
	re_path(r"check", CheckPay.as_view(), name="check"),
	
	# 订单支付 支付宝接口使用
	re_path(r"pay", OrderPayView.as_view(), name="pay"),
	
	# 订单提交
	re_path(r"commit", OredrCommit_badlock.as_view(), name="commit"),
	
	# 订单结算页面
	re_path(r"place", OrderPlaceInfo.as_view(), name="place")
	
]