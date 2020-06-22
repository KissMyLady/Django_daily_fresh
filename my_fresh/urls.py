from django.contrib import admin
from django.urls import path, re_path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^tinymce/', include('tinymce.urls')),    # 反向解析
    re_path(r'^users/',   include(("users.urls",  "users"),  namespace="users")),   # 反向解析
    re_path(r"^carts/",   include(("carts.urls",  "carts"),  namespace="carts")),   # 反向解析
    re_path(r"^orders/",  include(("orders.urls", "orders"), namespace="orders")),  # 反向解析
    re_path("^",          include(("goods.urls",  "goods"),  namespace="goods")),   # 反向解析
]
