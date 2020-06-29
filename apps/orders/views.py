from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse
from django.views import View
from utils.isLogin import LoginRequiredMixin
from django_redis import get_redis_connection
from goods.models import GoodsSKU
from users.models import Address
from orders.models import OrderInfo, OrderGoods
from django.db import transaction  # mysql事务
from datetime import datetime
from utils.Logging import Use_Loggin
import sys, os
from django.conf import settings
from alipay import AliPay


class OrderPlaceInfo(LoginRequiredMixin, View):
	def post(self, request):
		user = request.user  # mylady
		
		# 表单checkbox
		sku_ids = request.POST.getlist('sku_ids')  # [1,26]
		
		# 校验
		if not sku_ids:
			return redirect(reverse('carts:cart'))
		
		conn = get_redis_connection('default')
		cart_key = 'cart_%d' % user.id
		
		skus = list()
		
		# 保存总件数和总价格
		total_count = 0
		total_price = 0
		
		# 遍历sku_ids获取用户要购买的商品的信息
		for sku_id in sku_ids:
			
			# 根据商品的id获取商品的信息
			sku = GoodsSKU.objects.get(id=sku_id)
			
			# 获取用户所要购买的商品的数量
			raw_count = conn.hget(cart_key, sku_id)
			count = raw_count.decode('utf-8')
			
			# 计算商品的小计
			amount = sku.price * int(count)
			
			# 动态给sku增加属性count,保存购买商品的数量
			sku.count = count
			
			# 动态给sku增加属性amount,保存购买商品的小计
			sku.amount = amount
			
			skus.append(sku)
			
			# 累加 件数-价格
			total_count += int(count)
			total_price += amount
		
		# 运费: 实际开发的时候，属于一个子系统
		transit_price = 10  # 写死
		
		# 实付款
		total_pay = total_price + transit_price
		
		# 获取用户的收件地址
		addrs = Address.objects.filter(user=user)
		
		# 组织上下文
		sku_ids = ','.join(sku_ids)  # [1,25]->1,25
		context = {'skus': skus,
		           'total_count': total_count,
		           'total_price': total_price,
		           'transit_price': transit_price,
		           'total_pay': total_pay,
		           'addrs': addrs,
		           'sku_ids': sku_ids
		           }
		
		# 使用模板
		return render(request, 'place.html', context)
	
	def get(self, requset):
		return HttpResponse("仅支持post请求")
	

# 订单创建 悲观锁
class OredrCommit_badlock(LoginRequiredMixin, View):
	@transaction.atomic
	def post(self, request):
		logging = Use_Loggin()
		user = request.user
		
		if not user.is_authenticated:
			return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
		
		# 获取参数
		addr_id = request.POST.get('addr_id')
		pay_method = request.POST.get('pay_method')
		sku_ids = request.POST.get('sku_ids')  # 1,3
		
		# 校验
		if not all([addr_id, pay_method, sku_ids]):
			return JsonResponse({'res': 1, 'errmsg': '参数不完整'})
		
		# 校验支付方式
		if pay_method not in OrderInfo.PAY_METHODS.keys():
			return JsonResponse({'res': 2, 'errmsg': '非法的支付方式'})
		
		# 校验地址
		try:
			addr = Address.objects.get(id=addr_id)
		except Address.DoesNotExist:
			return JsonResponse({'res': 3, 'errmsg': '地址非法'})
		
		# todo: 创建订单核心业务
		
		# 组织参数
		# 订单id: 20171122181630+用户id
		order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)
		
		# 运费
		transit_price = 10
		
		# 总数目和总金额
		total_count = 0
		total_price = 0
		
		# 设置事务保存点
		save_id = transaction.savepoint()
		try:
			# todo: 向df_order_info表中添加一条记录
			order = OrderInfo.objects.create(order_id=order_id,
			                                 user=user,
			                                 addr=addr,
			                                 pay_method=pay_method,
			                                 total_count=total_count,
			                                 total_price=total_price,
			                                 transit_price=transit_price)
			
			# todo: 用户的订单中有几个商品，需要向df_order_goods表中加入几条记录
			conn = get_redis_connection('default')
			cart_key = 'cart_%d' % user.id
			
			sku_ids = sku_ids.split(',')
			for sku_id in sku_ids:
				# 获取商品的信息
				try:
					# select * from df_goods_sku where id=sku_id for update;
					sku = GoodsSKU.objects.select_for_update().get(id=sku_id)  # 使用悲观锁 阻塞
				except:
					transaction.savepoint_rollback(save_id)
					logging.error("%s订单创建失败, 由于商品不存在" % user)
					return JsonResponse({'res': 4, 'errmsg': '商品不存在'})
				
				print('user:%d stock:%d' % (user.id, sku.stock))
				
				# import time
				# time.sleep(3)
				
				# 从redis中获取用户所要购买的商品的数量
				count = conn.hget(cart_key, sku_id)
				
				# todo: 判断商品的库存
				if int(count) > sku.stock:
					transaction.savepoint_rollback(save_id)
					return JsonResponse({'res': 6, 'errmsg': '商品库存不足'})
				
				# todo: 向df_order_goods表中添加一条记录
				OrderGoods.objects.create(order=order, sku=sku, count=count, price=sku.price)
				
				# todo: 更新商品的库存和销量
				sku.stock -= int(count)
				sku.sales += int(count)
				sku.save()
				
				# todo: 累加计算订单商品的总数量和总价格
				amount = sku.price * int(count)
				total_count += int(count)
				total_price += amount
			
			# todo: 更新订单信息表中的商品的总数量和总价格
			order.total_count = total_count
			order.total_price = total_price
			order.save()
			
		except Exception as e:
			# 回滚到保存点
			transaction.savepoint_rollback(save_id)
			logging.error("用户%s下单失败, 在第%s行" % (user, sys._getframe().f_lineno))
			return JsonResponse({'res': 7, 'errmsg': '下单失败'})
		
		# 提交事务
		transaction.savepoint_commit(save_id)
		
		# todo: 清除用户购物车中对应的记录
		conn.hdel(cart_key, *sku_ids)
		
		return JsonResponse({'res': 5, 'message': '创建成功'})
	
	def get(self, request):
		return HttpResponse("None")


# 订单创建 乐观锁 没有锁的开销 冲突少使用
class OredrCommit_lucklock(LoginRequiredMixin, View):
	@transaction.atomic
	def post(self, request):
		logging = Use_Loggin()
		user = request.user
		
		if not user.is_authenticated:
			return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
		
		# 获取参数
		addr_id = request.POST.get('addr_id')
		pay_method = request.POST.get('pay_method')
		sku_ids = request.POST.get('sku_ids')  # 1,3
		
		# 校验
		if not all([addr_id, pay_method, sku_ids]):
			return JsonResponse({'res': 1, 'errmsg': '参数不完整'})
		
		# 校验支付方式
		if pay_method not in OrderInfo.PAY_METHODS.keys():
			return JsonResponse({'res': 2, 'errmsg': '非法的支付方式'})
		
		# 校验地址
		try:
			addr = Address.objects.get(id=addr_id)
		except Address.DoesNotExist:
			return JsonResponse({'res': 3, 'errmsg': '地址非法'})
		
		# todo: 创建订单核心业务
		
		# 组织参数
		# 订单id: 20171122181630+用户id
		order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)
		
		# 运费
		transit_price = 10
		
		# 总数目和总金额
		total_count = 0
		total_price = 0
		
		# 设置事务保存点
		save_id = transaction.savepoint()
		try:
			# todo: 向df_order_info表中添加一条记录
			order = OrderInfo.objects.create(order_id=order_id, user=user, addr=addr, pay_method=pay_method,
			                                 total_count=total_count, total_price=total_price,
			                                 transit_price=transit_price)
			
			# todo: 用户的订单中有几个商品，需要向df_order_goods表中加入几条记录
			conn = get_redis_connection('default')
			cart_key = 'cart_%d' % user.id
			
			sku_ids = sku_ids.split(',')
			for sku_id in sku_ids:
				for i in range(3):
					# 获取商品的信息
					try:
						# select * from df_goods_sku where id=sku_id for update;
						sku = GoodsSKU.objects.get(id=sku_id)
					except:
						transaction.savepoint_rollback(save_id)
						logging.error("%s订单创建失败, 由于商品不存在" % user)
						return JsonResponse({'res': 4, 'errmsg': '商品不存在'})
					
					print('user:%d stock:%d' % (user.id, sku.stock))
					
					# import time
					# time.sleep(5)
					
					# 从redis中获取用户所要购买的商品的数量
					count = conn.hget(cart_key, sku_id)
					
					# todo: 判断商品的库存
					if int(count) > sku.stock:
						transaction.savepoint_rollback(save_id)
						return JsonResponse({'res': 6, 'errmsg': '商品库存不足'})
					
					# todo: 更新商品的库存和销量
					origin_stock = sku.stock
					new_stock = origin_stock - int(count)
					new_sales = sku.sales + int(count)
					
					# update df_goods_sku set stock=new_stock, sales=new_sales where id=sku_id and stock = origin_stock
					res = GoodsSKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
					# 返回受影响的行数
					if res == 0:
						if i == 2:  # 改了库存, 再次尝试
							# 尝试的第3次
							transaction.savepoint_rollback(save_id)
							return JsonResponse({'res': 7, 'errmsg': '下单失败2'})
						continue
							
					# todo: 向df_order_goods表中添加一条记录
					OrderGoods.objects.create(order=order,
					                          sku=sku,
					                          count=count,
					                          price=sku.price)
					
					# todo: 累加计算订单商品的总数量和总价格
					amount = sku.price * int(count)
					total_count += int(count)
					total_price += amount
					
					break
			
			# todo: 更新订单信息表中的商品的总数量和总价格
			order.total_count = total_count
			order.total_price = total_price
			order.save()
		
		except Exception as e:
			# 回滚到保存点
			transaction.savepoint_rollback(save_id)
			logging.error("用户%s下单失败, 在第%s行" % (user, sys._getframe().f_lineno))
			return JsonResponse({'res': 7, 'errmsg': '下单失败'})
		
		# 提交事务
		transaction.savepoint_commit(save_id)
		
		# todo: 清除用户购物车中对应的记录
		conn.hdel(cart_key, *sku_ids)
		
		return JsonResponse({'res': 5, 'message': '创建成功'})
	
	def get(self, request):
		return HttpResponse("None")
	

# 支付接口
class OrderPayView(View):
	def post(self, request):
		user = request.user
		
		print(request.POST)
		
		if not user.is_authenticated:
			return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
		
		order_id = request.POST.get('order_id')
		
		# 校验
		if not order_id:
			return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})

		try:
			order = OrderInfo.objects.get(order_id=order_id,
			                              user=user,
			                              pay_method=3,
			                              order_status=1)
		except OrderInfo.DoesNotExist:
			return JsonResponse({'res': 2, 'errmsg': '订单错误'})

		# 路径拼接
		BASE_DIR = os.path.dirname(os.path.abspath(__file__))
		alipay_public_key_path = os.path.join(os.path.join(BASE_DIR, "keys_pay"), 'alipay_public_key.pem')
		app_private_key_path = os.path.join(os.path.join(BASE_DIR, "keys_pay"), 'app_private_key.pem')
		print("alipay_public_key_path: ", alipay_public_key_path)
		print("app_private_key_path: ", app_private_key_path)
		
		# 读取密钥数据
		with open(alipay_public_key_path, "r", encoding="utf-8") as f:
			alipay_public_key_path_read = f.read()
		
		with open(app_private_key_path, "r", encoding="utf-8") as f:
			app_private_key_path_read = f.read()
		
		# 初始化
		alipay_client = AliPay(appid=settings.ALIPAY_APIT_NUMS,  # 沙箱环境的apid
		                       app_notify_url=None,  # 回调, 不需要回调
		                       app_private_key_string=app_private_key_path_read,  # 给路径即可
		                       alipay_public_key_string=alipay_public_key_path_read,
		                       sign_type="RSA2",     # RSA或者 RSA2
		                       debug=False)
		
		# 电脑网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
		total_pay = order.total_price + order.transit_price  # Decimal
		print("支付中的order_id: ", order_id, type(order_id))
		order_string = alipay_client.api_alipay_trade_page_pay(
						out_trade_no=order_id,        # 订单id
						total_amount=str(total_pay),  # 支付总金额
						subject='天天生鲜%s' % order_id,
						# return_url="http://127.0.0.1:8000/orders/check",  # 支付成功后, 跳转页面
						return_url=None,
						notify_url=None     # 可选, 不填则使用默认notify url
		)
		
		# 构建跳转地址
		pay_url = settings.ALIPAY_URL_DEV_PRIFIX + order_string
		return JsonResponse({'res': 3, 'pay_url': pay_url})


# 支付校验 /orders/check
class CheckPay(View):
	def post(self, request):
		from time import sleep
		sleep(15)
		
		logging = Use_Loggin()
		user = request.user
		
		if not user.is_authenticated:
			return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
		
		# 接收参数
		order_id = request.POST.get('order_id')
		print("order_id: ", order_id)
		
		# 校验参数
		if not order_id:
			return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})
		
		try:
			order = OrderInfo.objects.get(order_id=order_id,
			                              user=user,
			                              pay_method=3,
			                              order_status=1)
			
		except OrderInfo.DoesNotExist:
			return JsonResponse({'res': 2, 'errmsg': '订单错误'})
	
		KEY_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
		alipay_public_key_path = os.path.join(os.path.join(KEY_BASE_DIR, "keys_pay"), 'alipay_public_key.pem')
		app_private_key_path = os.path.join(os.path.join(KEY_BASE_DIR, "keys_pay"), 'app_private_key.pem')

		# 读取密钥数据
		with open(alipay_public_key_path, "r", encoding="utf-8") as f:
			alipay_public_key_path_read = f.read()
		
		with open(app_private_key_path, "r", encoding="utf-8") as f:
			app_private_key_path_read = f.read()
		
		# 初始化
		try:
			alipay_client = AliPay(appid=settings.ALIPAY_APIT_NUMS,  # 沙箱环境的apid
			                       app_notify_url=None,    # 回调, 不需要回调
			                       app_private_key_string=app_private_key_path_read,  # 给路径即可
			                       alipay_public_key_string=alipay_public_key_path_read,
			                       sign_type="RSA2",     # RSA或者 RSA2
			                       debug=False)
		except:
			logging.error("订单信息回调信息获取失败, 第 %s行" %(sys._getframe().f_lineno))
			return JsonResponse({"res": 3, "errmsg": "订单信息回调失败"})
		
		# 调用支付宝的交易查询接口
		while True:
			try:
				response = alipay_client.api_alipay_trade_query(out_trade_no=order_id)
				print("type(response): ", type(response), "response: ", response)
			except Exception as e:
				print(">"*10, e)
				logging.error("支付错误 %s" % (sys._getframe().f_lineno))
				return JsonResponse({"res": 3, "errmsg": "支付错误"})
		
			code = response.get('code')
			print("code: ", code)
			print("response.get('trade_status') ", response.get('trade_status'))
			
			if code == '10000' and response.get('trade_status') == 'TRADE_SUCCESS':
				trade_no = response.get('trade_no')
				
				# 更新
				order.trade_no = trade_no
				order.order_status = 4 # 待评价
				order.save()
				return JsonResponse({'res': 3, 'message': '支付成功'})
			
			elif code == '40004' or (code == '10000' and response.get('trade_status') == 'WAIT_BUYER_PAY'):
				# 等待买家付款
				# 业务处理失败，可能一会就会成功
				import time
				time.sleep(5)
				continue
				
			else:
				# 支付出错
				logging.error("支付错误 在第%s行" %(sys._getframe().f_lineno))
				print(code)
				return JsonResponse({'res': 4, 'errmsg': '支付失败'})
	
	def put(self, request):
		print("put请求 >>>>>>>>>>>>>>>>>>>")
		logging = Use_Loggin()
		user = request.user
		print("put, user: ", user)
		
		print("PUT: ", request.PUT)
		
		if not user.is_authenticated:
			return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
		
		# 接收参数
		order_id = request.POST.get('order_id')
		print("order_id: ", order_id)
		
		# 校验参数
		if not order_id:
			return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})
		
		try:
			order = OrderInfo.objects.get(order_id=order_id, user=user, pay_method=3, order_status=1)
		
		except OrderInfo.DoesNotExist:
			return JsonResponse({'res': 2, 'errmsg': '订单错误'})
		
		KEY_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
		alipay_public_key_path = os.path.join(os.path.join(KEY_BASE_DIR, "keys_pay"), 'alipay_public_key.pem')
		app_private_key_path = os.path.join(os.path.join(KEY_BASE_DIR, "keys_pay"), 'app_private_key.pem')
		
		# 读取密钥数据
		with open(alipay_public_key_path, "r", encoding="utf-8") as f:
			alipay_public_key_path_read = f.read()
		
		with open(app_private_key_path, "r", encoding="utf-8") as f:
			app_private_key_path_read = f.read()
		
		# 初始化
		try:
			alipay_client = AliPay(appid=settings.ALIPAY_APIT_NUMS,  # 沙箱环境的apid
			                       app_notify_url=None,  # 回调, 不需要回调
			                       app_private_key_string=app_private_key_path_read,  # 给路径即可
			                       alipay_public_key_string=alipay_public_key_path_read, sign_type="RSA2",
			                       # RSA或者 RSA2
			                       debug=False)
		except:
			logging.error("订单信息回调信息获取失败, 第 %s行" % (sys._getframe().f_lineno))
			return JsonResponse({"res": 3, "errmsg": "订单信息回调失败"})
		
		# 借助工具验证参数的合法性
		# 如果确定参数是支付宝的，返回True，否则返回false
		# try:
		# 	result = alipay_client.verify(alipay_dict, alipay_signAture)
		# except Exception as e:
		# 	logging.error("支付回调失败")
		# 	return JsonResponse({"res": 3, "errmsg": "支付错误"})
		
		# 调用支付宝的交易查询接口
		while True:
			try:
				response = alipay_client.api_alipay_trade_query(order_id)
				print("type(response): ", type(response), "response: ", response)
			except Exception as e:
				print(">" * 10, e)
				logging.error("支付错误 %s" % (sys._getframe().f_lineno))
				return JsonResponse({"res": 3, "errmsg": "支付错误"})
			# response = {
			#         "trade_no": "2017032121001004070200176844", # 支付宝交易号
			#         "code": "10000", # 接口调用是否成功
			#         "invoice_amount": "20.00",
			#         "open_id": "20880072506750308812798160715407",
			#         "fund_bill_list": [
			#             {
			#                 "amount": "20.00",
			#                 "fund_channel": "ALIPAYACCOUNT"
			#             }
			#         ],
			#         "buyer_logon_id": "csq***@sandbox.com",
			#         "send_pay_date": "2017-03-21 13:29:17",
			#         "receipt_amount": "20.00",
			#         "out_trade_no": "out_trade_no15",
			#         "buyer_pay_amount": "20.00",
			#         "buyer_user_id": "2088102169481075",
			#         "msg": "Success",
			#         "point_amount": "0.00",
			#         "trade_status": "TRADE_SUCCESS", # 支付结果
			#         "total_amount": "20.00"
			# }
			
			code = response.get('code')
			print("code: ", code)
			print("response.get('trade_status') ", response.get('trade_status'))
			
			if code == '10000' and response.get('trade_status') == 'TRADE_SUCCESS':
				trade_no = response.get('trade_no')
				
				# 更新
				order.trade_no = trade_no
				order.order_status = 4  # 待评价
				order.save()
				return JsonResponse({'res': 3, 'message': '支付成功'})
			
			elif code == '40004' or (code == '10000' and response.get('trade_status') == 'WAIT_BUYER_PAY'):
				# 等待买家付款
				# 业务处理失败，可能一会就会成功
				import time
				time.sleep(5)
				continue
			
			else:
				# 支付出错
				logging.error("支付错误 在第%s行" % (sys._getframe().f_lineno))
				print(code)
				return JsonResponse({'res': 4, 'errmsg': '支付失败'})
	
	# 分割url, 转换成字典, 提取sign值
	def to_dict(self, abc):
		str_abc = str(abc)
		print("type(str_abc): ", type(str_abc), "str_abc: >>>>>>>>>>>", str_abc)
		if "?" in str_abc:
			raw_abc = str_abc.split("?")[1]
		else:
			raw_abc = str_abc
			
		to_dict = raw_abc.split("&")
		
		result_dict = dict()
		for i in to_dict:
			if "total_amount" in i:
				value = float(i.split("=")[1])
				result_dict["%s" % i.split("=")[0]] = value
				continue
				
			result_dict["%s" % i.split("=")[0]] = i.split("=")[1]
		
		sign = result_dict.pop("sign")
		print("sign: >>>>>>>>>>>>", sign)
		print("result_dict>>>>>>>", result_dict)
		return result_dict, sign
		
	def get(self, request):
		logging = Use_Loggin()
		user = request.user
		
		if not user.is_authenticated:
			return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

		
		full_path = request.get_full_path()
		print("full_path: >>>>>", full_path)
		# print(full_path)  # 打印出全路径（路径和参数）
		# print(request.path_info)  # 取当前请求的路径
		
		alipay_dict, alipay_signAture = self.to_dict(full_path)
		print("alipay_dict: ", alipay_dict)
		print("alipay_signAture: ", alipay_signAture)
		
		# 对支付宝的数据进行分离  提取出支付宝的签名参数sign 和剩下的其他数据
		# alipay_signAture = alipay_dict.pop("sign")  # 计算结果是很长的字符串
		
		# 路径拼接
		KEY_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
		alipay_public_key_path = os.path.join(os.path.join(KEY_BASE_DIR, "keys_pay"), 'alipay_public_key.pem')
		app_private_key_path = os.path.join(os.path.join(KEY_BASE_DIR, "keys_pay"), 'app_private_key.pem')
		
		# 读取密钥数据
		with open(alipay_public_key_path, "r", encoding="utf-8") as f:
			alipay_public_key_path_read = f.read()
		
		with open(app_private_key_path, "r", encoding="utf-8") as f:
			app_private_key_path_read = f.read()
		
		try:
			alipay_client = AliPay(appid=settings.ALIPAY_APIT_NUMS,
			                       app_notify_url=None,  # 默认回调url
			                       app_private_key_string=app_private_key_path_read,  # 私钥
			                       alipay_public_key_string=alipay_public_key_path_read,  # 支付宝的公钥, 验证支付宝回传消息使用, 不是你自己的公钥,
			                       sign_type="RSA2",  # RSA 或者 RSA2
			                       debug=False)  # 默认False
			
		except Exception as e:
			logging.error("订单信息回调信息获取失败")
			# return JsonResponse({"err":0, "errmsg"="订单信息回调失败"})
		
		# 借助工具验证参数的合法性
		# 如果确定参数是支付宝的，返回True，否则返回false
		try:
			print("开始校验alipay_client sing值")
			result = alipay_client.verify(alipay_dict, alipay_signAture)  # True
			
		except Exception as e:
			print("e: >>>>>>>>>", e)
			logging.error("支付回调失败")
			return JsonResponse({"err": 0, "errmsg": "查询失败"})
		
		order_id = alipay_dict.get("out_trade_no")  # 流水号
		trade_no = alipay_dict.get("trade_no")      # 支付宝的交易号

		# 校验参数
		if not order_id:
			return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})
		try:
			print("order_id: ", order_id, "user: ", user)
			order = OrderInfo.objects.get(order_id=order_id, user=user, pay_method=3, order_status=1)
		except OrderInfo.DoesNotExist:
			return JsonResponse({'res': 2, 'errmsg': '订单错误'})
		
		if result:
			# 修改数据库的订单状态信息
			print("查询成功, 修改数据库数据")
			trade_no = alipay_dict.get('trade_no')
			
			# 更新
			order.trade_no = trade_no
			order.order_status = 2  # 待发货
			order.save()
			
			return JsonResponse({'res': 3, 'message': '支付成功'})

		
# 订单评价
class Comment(LoginRequiredMixin, View):
	def get(self, request, order_id):
		user = request.user
		
		# 校验
		if not order_id:
			return redirect(reverse('users:order'))
		
		try:
			order = OrderInfo.objects.get(order_id=order_id, user=user)
		except OrderInfo.DoesNotExist:
			return redirect(reverse("users:order"))
		
		# 根据订单的状态获取订单的状态标题
		order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
		
		# 获取订单商品信息
		order_skus = OrderGoods.objects.filter(order_id=order_id)
		for order_sku in order_skus:
			# 计算商品的小计
			amount = order_sku.count * order_sku.price
			# 动态给order_sku增加属性amount,保存商品小计
			order_sku.amount = amount
			
		# 动态给order增加属性order_skus, 保存订单商品信息
		order.order_skus = order_skus
		
		# 使用模板
		return render(request, "order_comment.html", {"order": order})
	
	def post(self, request, order_id):
		"""处理评论内容"""
		user = request.user
		
		# 校验
		if not order_id:
			return redirect(reverse('users:order'))
		
		try:
			order = OrderInfo.objects.get(order_id=order_id, user=user)
		except OrderInfo.DoesNotExist:
			return redirect(reverse("users:order"))
		
		# 获取评论条数
		total_count = request.POST.get("total_count")
		total_count = int(total_count)
		
		# 循环获取订单中商品的评论内容
		for i in range(1, total_count + 1):
			# 获取评论的商品的id
			sku_id = request.POST.get("sku_%d" % i)  # sku_1 sku_2
			# 获取评论的商品的内容
			content = request.POST.get('content_%d' % i, '')  # cotent_1 content_2 content_3
			try:
				order_goods = OrderGoods.objects.get(order=order, sku_id=sku_id)
			except OrderGoods.DoesNotExist:
				continue
			
			order_goods.comment = content
			order_goods.save()
		
		order.order_status = 5  # 已完成
		order.save()
		
		return redirect(reverse("users:order", kwargs={"page": 1}))