# 文件名: Django_today -> isLogin
# 创建时间: 2020/6/22 1:59
from django.contrib.auth.decorators import login_required  # 函数直接使用


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        # 调用父类的as_view
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)