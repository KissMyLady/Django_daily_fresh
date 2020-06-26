from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.http import JsonResponse
from goods.models import GoodsSKU
from django_redis import get_redis_connection
from utils.Logging import Use_Loggin
import sys
from django.views import View
from utils.isLogin import LoginRequiredMixin


def createsession(request):
    request.session['name'] = 'xiaowang'
    return HttpResponse("session设置")


# 购物车页面显示 /carts/cart
class CartInfoShow(LoginRequiredMixin, View):
    def get(self, request):
        logging = Use_Loggin()
        user = request.user
        
        conn = get_redis_connection("default")
        cart_key = "cart_%d" % (user.id)
        cart_dict = conn.hgetall(cart_key)
    
        skus = list()
        total_count = 0
        total_price = 0
        
        for sku_id, count in cart_dict.items():
            # 获取信息
            sku = GoodsSKU.objects.get(id=sku_id)
            
            # 计算金额
            amount = sku.price * int(count)
            
            # 动态增加属性
            sku.amount = amount
            sku.count = count.decode("utf-8")
    
            # 添加
            skus.append(sku)
            total_count += int(count.decode("utf-8"))
            total_price += amount
            
        # 组织上下文
        context = {'total_count': total_count,
                   'total_price': total_price,
                   'skus': skus}
        
        return render(request, "user_center_cart.html", context)
    
    def post(self, request):
        return HttpResponse("post请求, 仅仅支持get请求")


# 购物车添加接口
def addCart(request):
    if request.method == "POST":
        # 获取日志对象
        logging = Use_Loggin()
        
        # 获取当前用户
        user = request.user
        
        # 判定是否登录
        if user.is_authenticated:
            data = {"res": 0, "messg": "请登录"}
            JsonResponse(data)
        
        # 获取参数
        sku_id = request.POST.get("sku_id")
        count =  request.POST.get("count")
        
        # 校验
        if not all([sku_id, count]):
            return JsonResponse({"res": 0, "messg": "请登录"})
        try:
            count = int(count)
        except:
            return JsonResponse({"res": 2, "messg": "商品数目错误"})

        # 查询
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
            print("sku: ", sku, "type(sku): ", type(sku))
        except Exception as e:
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})
        
        # 先尝试获取 sku_id的值 -> hget cart_key 属性
        # 如果 sku_id在hash中不存在，hget返回None
        try:
            conn = get_redis_connection("default")  # 获取redis连接
            print("type(conn): ", type(conn), "conn: ", conn)
            
            cart_key = "cart_%d" % user.id          # 获取购物车redis存储的用户数据
            print("cart_key: ", cart_key, "sku_id: ", sku_id)
            
            # 如果拿不到, 返回None
            raw_cart_count = conn.hget(name=cart_key, key=sku_id)
            
            print("type(raw_cart_count): ", type(raw_cart_count), "raw_cart_count: ", raw_cart_count)
            
            if raw_cart_count == None:
                cart_count = 0
            else:
                cart_count = int(raw_cart_count.decode("utf-8"))
            
            print("cart_count: ", cart_count, type(cart_count))
            if cart_count:
                # 累计购物车数量, 比对库存数量
                count += int(cart_count)
                
        except Exception as e:
            logging.error("redis获取的购物车数不是int类型 在第 %s行" % sys._getframe().f_lineno)
            return JsonResponse({'res': 8, 'errmsg': '服务器错误'})
     
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})
        
        # 设置hash中sku_id对应的值
        # hset->如果sku_id已经存在，更新数据， 如果sku_id不存在，添加数据
        conn.hset(cart_key, sku_id, count)

        # 计算用户购物车商品的条目数
        total_count = conn.hlen(cart_key)

        # 返回应答
        return JsonResponse({'res': 5,
                             'total_count': total_count,
                             'message': '添加成功'})
    
    if request.method == "GET":
        return HttpResponse("GET请求方式, 但仅限POST请求")
    
    else:
        return HttpResponse("其他请求方式, 仅限POST请求")
    

# 购物车更新接口
class UpdataAjax(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        logging = Use_Loggin()
        
        sku_id = request.POST.get("sku_id")
        count = request.POST.get("count")
        print("sku_id & count: ", sku_id, count)
        
        if not all([sku_id, count]):
            return JsonResponse({"res": 1, "errmsg": "数据不完整"})
        
        try:
            count = int(count)
        except:
            return JsonResponse({"res": 2, "errmsg": "商品数据错误"})
        
        # 校验商品是否存在
        try:
            sku = GoodsSKU.objectsget(id=sku_id)
        except:
            return JsonResponse({"res": 3, "errmsg":"商品不存在"})
        
        conn = get_redis_connection("default")
        cart_key = "cart_%d" % (user.id)
        
        if count > sku.stock:
            return JsonResponse({"res": 4, "errmsg": "商品库存不足"})
        
        # 更新
        conn.hset(name=cart_key, key=sku_id, value=count)

        # 计算用户购物车中商品的总件数 {'1':5, '2':3}
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)

        # 返回应答
        return JsonResponse({'res': 5, 'total_count': total_count, 'message': '更新成功'})
    
    def get(self, request):
        return HttpResponse("仅限POST请求")
    

# 删除购物车记录
# 采用ajax post请求
# 前端需要传递的参数:商品的id(sku_id)
# /cart/delete
class DeleteAjax(LoginRequiredMixin, View):
    def post(self, request):
        logging = Use_Loggin()
        user = request.user
        
        # 接收参数
        sku_id = request.POST.get('sku_id')

        # 数据的校验
        if not sku_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的商品id'})

        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res':2, 'errmsg':'商品不存在'})


        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % (user.id)

        # 删除 hdel
        conn.hdel(cart_key, sku_id)

        # 计算用户购物车中商品的总件数 {'1':5, '2':3}
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)

        # 返回应答
        return JsonResponse({'res': 3, 'total_count': total_count, 'message': '删除成功'})

