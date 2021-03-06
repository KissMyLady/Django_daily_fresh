from django.db import models
# Create your models here.


class BaseModel(models.Model):
    '''模型抽象基类'''
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True,     verbose_name='更新时间')
    is_delete = models.BooleanField(default=False,        verbose_name='删除标记')

    class Meta:
        # 说明是一个抽象模型类
        abstract = True


# 订单模型
class OrderInfo(BaseModel):
    PAY_METHODS = {
        '1': "货到付款",
        '2': "微信支付",
        '3': "支付宝",
        '4': '银联支付'
    }
    
    PAY_METHOD_CHOICES = (
        (1, '货到付款'),
        (2, '微信支付'),
        (3, '支付宝'),
        (4, '银联支付')
    )
    
    PAY_METHODS_ENUM = {
        "CASH": 1,
        "ALIPAY": 2}

    ORDER_STATUS = {
        1: '待支付',
        2: '待发货',
        3: '待收货',
        4: '待评价',
        5: '已完成'}
    
    ORDER_STATUS_ENUM = {
        "UNPAID": 1,
        "UNSEND": 2,
        "UNRECEIVED": 3,
        "UNCOMMENT": 4,
        "FINISHED": 5}
    
    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '待发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已完成')
    )
    order_id = models.CharField(max_length=128, primary_key=True, verbose_name='订单id')                      # 订单id
    user = models.ForeignKey('users.User', verbose_name='用户', on_delete=models.CASCADE)                     # 用户
    addr = models.ForeignKey('users.Address', verbose_name='地址', on_delete=models.CASCADE)                  # 地址
    pay_method = models.SmallIntegerField(choices=PAY_METHOD_CHOICES, default=3, verbose_name='支付方式')      # 支付方式
    total_count = models.IntegerField(default=1, verbose_name='商品数量')                                      # 商品数量
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品总价')                # 商品总价
    transit_price = models.DecimalField(max_digits=10, decimal_places=2,verbose_name='订单运费')               # 订单运费
    order_status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, default=1, verbose_name='订单状态')  # 订单状态
    trade_no = models.CharField(max_length=128, verbose_name='支付编号')                                       # 流水号

    class Meta:
        db_table = 'df_order_info'
        verbose_name = '订单'
        verbose_name_plural = verbose_name


class OrderGoods(BaseModel):
    '''订单商品模型类'''
    order = models.ForeignKey('OrderInfo',     verbose_name='订单', on_delete=models.CASCADE)
    sku = models.ForeignKey('goods.GoodsSKU',  verbose_name='商品SKU', on_delete=models.CASCADE)
    count = models.IntegerField(default=1,     verbose_name='商品数目')
    price = models.DecimalField(max_digits=10, verbose_name='商品价格', decimal_places=2, )
    comment = models.CharField(max_length=256, verbose_name='评论')

    class Meta:
        db_table = 'df_order_goods'
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name