import re, sys
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .models import User
from Logging import Use_Loggin
from itsdangerous import TimedJSONWebSignatureSerializer as safe
from users.models import Address, User
from utils.isLogin import LoginRequiredMixin
from django_redis import get_redis_connection
from goods.models import GoodsSKU


# 登录逻辑
class LoginView(View):
	def get(self, request):
		if 'username' in request.COOKIES:
			username = request.COOKIES.get("username")
			try:
				username = username.decode("utf-8")
			except:
				username = "请输入用户名"
			checked = 'checked'
		else:
			username = ""
			checked = ""
		return render(request, "login.html", {"username": username, "checked": checked})
	
	def post(self, request):
		logging = Use_Loggin()
		# 提取数据
		username = request.POST.get('username')
		password = request.POST.get('pwd')
		
		# 校验 使用 django内置用户认证模块
		user = authenticate(username=username, password=password)
		
		if user is not None:
			if user.is_active:
				login(request, user)
				# 表单可能没有action, 会跳到默认的地址, 这里获取拼接, 如果没有, 设置默认的
				next_url = request.GET.get("next", reverse("goods:index"))
				response = redirect(next_url)
				
				# 记住用户名
				remember = request.POST.get('remember')
				if remember == 'on':
					try:
						en_username = username.encode("utf-8")  # 数据库可能报错
						response.set_cookie('username', en_username, max_age=settings.LOGIN_COOKIE_EXPIRE)
					except:
						logging.error("保存cookie错误, 可能是转码问题, 在第 %s行" % (sys._getframe().f_lineno))
						return render(request, 'login.html', {'errmsg': '保存cookie错误'})
				else:
					try:
						response.delete_cookie('username')
					except:
						logging.error("删除cookie错误, 可能是数据库或缓存问题, 在第 %s行" % (sys._getframe().f_lineno))
						pass
					
				return response
			else:
				return render(request, 'login.html', {'errmsg': '您的账户未激活'})
		else:
			return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


# 退出登录逻辑
def LogoutView(request):
	if request.method == "GET":
		logout(request)
		return redirect(reverse("goods:index"))
	else:
		return HttpResponse("仅限get请求退出登录")


# 注册逻辑: /users/register
def register(request):
	# 获取日志接口
	logging = Use_Loggin()
	if request.method == 'GET':
		return render(request, 'register.html')
	else:
		# 获取参数
		username = request.POST.get('user_name')
		password = request.POST.get('pwd')
		passwor2 = request.POST.get("cpwd")
		email =    request.POST.get('email')
		allow =    request.POST.get('allow')  # 同意协议
		
		# 校验
		if not all([username, password, passwor2, email]):
			# 数据不完整
			return render(request, 'register.html', {'errmsg': '数据不完整'})
		
		if password != passwor2:
			return render(request, 'register.html', {'errmsg': '二次输入密码不一致'})
		
		# 校验
		if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
			return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
		
		if allow != 'on':
			return render(request, 'register.html', {'errmsg': '请同意协议'})
		
		# 校验
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			user = None
		
		if user:
			return render(request, 'register.html', {'errmsg': '用户名已存在'})
		
		# 保存
		user = User.objects.create_user(username, email, password)
		user.is_active = 0
		user.save()
		
		# 加密，生成token
		serializer = safe(settings.SECRET_KEY, 3600)
		info = {'confirm': user.id}
		token = serializer.dumps(info)  # bytes
		token = token.decode()
		
		# 异步发邮件
		# try:
		#   from celery_tasks import send_register_active_email
		# 	send_register_active_email.delay(email, username, token)
		# 	return redirect(reverse('goods:index'))
		# except Exception as e:
		# 	logging.error("异步发送邮件失败, 使用同步发送")
		
		# 使用同步发送
		subject = '天天生鲜欢迎信息'
		message = 'message'
		sender = settings.EMAIL_FROM
		receiver = [email]
		html_message = '<h1>%s, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a ' \
		               'href="http://127.0.0.1:8000/users/active/%s">http://127.0.0.1:8000/users/active/%s</a>' % (
		username, token, token)
		from django.core.mail import send_mail
		send_mail(subject, message, sender, receiver, html_message=html_message)
		
		# return HttpResponse(html_message)
		return redirect(reverse('goods:index'))
	

# 邮箱激活 /users/active/(?P<token>.*)$
class ActivateUserMail(View):
	def get(self, request, token):
		from django.conf import settings
		safe_obj = safe('{}'.format(settings.SECRET_KEY), settings.EMAIL_ACITVATE_EXPIRE)
		try:
			token = token.encode('utf-8')  # <class 'bytes'>
			info = safe_obj.loads(token)   # 解密
			user_id = info['confirm']      # 数字
			
			user = User.objects.get(id=user_id)
			user.is_active = True
			user.save()
			from django.http import HttpResponse
			return HttpResponse('校验成功')  # return redirect('user/login')
		
		except:
			from django.http import HttpResponse
			return HttpResponse('激活链接已失效')
	
	def post(self, request, *args, **kwargs):
		return HttpResponse('此激活方式只允许post请求')
	
	
# 使用类视图demo
class ViewUserLogin(View):
	def get(self, reqeust, *args, **kwargs):
		return HttpResponse("类视图get请求")
	
	def post(self, request, *args, **kwargs):
		return HttpResponse("类视图post请求")
	

# 用户中心界面
class UserInfoView(LoginRequiredMixin, View):
	'''用户中心-信息页'''
	def get(self, request):
		user = request.user
		address = Address.objects.get_default_address(user)
		
		# 获取用户的历史浏览记录
		con = get_redis_connection('default')
		history_key = 'history_%d' % user.id

		# 获取用户最新浏览的5个商品的id
		sku_ids = con.lrange(history_key, 0, 4)  # [2,3,1]
		
		# 从数据库中查询用户浏览的商品的具体信息
		# 遍历获取用户浏览的商品信息
		goods_li = []
		for id in sku_ids:
			goods = GoodsSKU.objects.get(id=id)
			goods_li.append(goods)
		
		# # 组织上下文
		context = {'page': 'user',
		 		   'address': address,
		           "goods_li": goods_li}
		
		# 除了给模板文件传递的模板变量之外，django框架会把request.user也传给模板文件
		return render(request, 'user_center_info.html', context)


# 用户订单页面
class UserOrderView(LoginRequiredMixin, View):
	def get(self, request):
		return render(request, "user_center_order.html", {"page": "order"})

	
# 森民路 燕子街 36号兴旺超市代收
# 用户地址页面
class UserAddressView(LoginRequiredMixin, View):
	def get(self, request):
		user = request.user
		
		try:
			address = Address.objects.get_default_address(user)
			print("自定义模型类方法 address: ", address)
		except:
			address = None
		
		return render(request, "user_center_address.html", {"page": "address", "address": address})
	
	def post(self, request):
		
		# 获取参数
		receiver = request.POST.get("receiver")   # 收货人
		addr = request.POST.get("addr")           # 地址
		zip_code = request.POST.get("zip_code")   # 邮编
		phone = request.POST.get("phone")         # 手机号
	
		if not all([receiver, addr, zip_code, phone]):
			return render(request, "user_center_address.html", {"page": "address",
			                                                    "errmsg": "信息填写不完整"})
		
		# 校验手机 11位手机号 132 0000 0000
		if not re.match(r"^1[3|4|5|7|8][0-9]{9}$", phone):
			return render(request, "user_center_address.html", {"page": "address",
			                                                    "errmsg": "手机填写不正确"})
		
		# 保存
		user = request.user
		
		# 打开models.py 自定义(方法)模型管理器类
		address = Address.objects.get_default_address(user)
		print("address是否有默认地址? : ", address)
		if address is None:
			is_default = True
		else:
			is_default = False
		
		# 保存
		try:
			Address.objects.create(user=user,
			                       receiver=receiver,
			                       addr=addr,
			                       zip_code=zip_code,
			                       phone=phone,
			                       is_default=is_default)
		except:
			return render(request, "user_center_address.html", {"page": "address",
			                                                    "errmsg": "保存错误, 请核对地址是否填写错误"})
		
		# 返回 刷新
		return redirect(reverse("users:address"))
