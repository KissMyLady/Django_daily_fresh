# 文件名: Django_today -> urls
# 创建时间: 2020/6/21 0:48
from django.urls import path, re_path, include
from users import views

# 类视图
from users.views import ViewUserLogin
from users.views import ActivateUserMail
from users.views import LoginView
from users.views import UserInfoView, UserOrderView, UserAddressView
from django.contrib.auth.decorators import login_required


urlpatterns = [
	
	# 用户中心
	re_path(r"^info",    UserInfoView.as_view(),    name="user"),   # 用户中心页面
	re_path(r"^order",   UserOrderView.as_view(),   name="order"),  # 订单页面 购物车
	re_path(r"^address", login_required(UserAddressView.as_view()), name="address"),  # 地址页面
	
	re_path(r"^login",    LoginView.as_view(), name="login"),     # 登录
	re_path(r"^logout",   views.LogoutView,    name="logout"),    # 退出登录
	re_path(r"^register", views.register,      name="register"),  # 注册页面
	
	re_path(r"^active/(?P<token>.*)$", ActivateUserMail.as_view(), name="active"),  # 邮箱激活
	path("demo",   ViewUserLogin.as_view(), name="demo")       # 使用类视图 demo
]