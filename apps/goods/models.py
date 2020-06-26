from django.db import models
from tinymce.models import HTMLField


class BaseModel(models.Model):
    '''模型抽象基类'''
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True,     verbose_name='更新时间')
    is_delete = models.BooleanField(default=False,        verbose_name='删除标记')

    class Meta:
        # 说明是一个抽象模型类
        abstract = True


class GoodsType(BaseModel):
    '''商品类型模型类'''
    name =  models.CharField(max_length=20,      verbose_name='种类名称')
    logo =  models.CharField(max_length=20,      verbose_name='标识')
    image = models.ImageField(upload_to='type',  verbose_name='商品类型图片')

    class Meta:
        db_table = 'df_goods_type'
        verbose_name = '商品种类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsSKU(BaseModel):
    '''商品SKU模型类'''
    status_choices = (
        (0, '下线'),
        (1, '上线'),
    )
    type =  models.ForeignKey('GoodsType',       verbose_name='商品种类', on_delete=models.CASCADE)
    goods = models.ForeignKey('Goods',           verbose_name='商品SPU', on_delete=models.CASCADE)
    name =  models.CharField(max_length=20,      verbose_name='商品名称')
    desc =  models.CharField(max_length=256,     verbose_name='商品简介')
    price = models.DecimalField(max_digits=10,   verbose_name='商品价格', decimal_places=2)
    unite = models.CharField(max_length=20,      verbose_name='商品单位')
    image = models.ImageField(upload_to='goods', verbose_name='商品图片')
    stock = models.IntegerField(default=1,       verbose_name='商品库存')
    sales = models.IntegerField(default=0,       verbose_name='商品销量')
    status= models.SmallIntegerField(default=1,  verbose_name='商品状态', choices=status_choices)
    
    def stockName(self):
        return self.stock
    
    def typeName(self):
        return self.type
    
    def titleName(self):
        return self.name
    
    def salesName(self):
        return self.sales
    
    # titleName.admin_order_field = 'name'  对name进行排序
    titleName.short_description = '商品SKU名称'
    typeName.short_description = '商品种类'
    stockName.short_description = '库存'
    salesName.short_description = '销量'
    salesName.admin_order_field = 'sales'
    
    class Meta:
        db_table = 'df_goods_sku'
        verbose_name = '商品'
        verbose_name_plural = verbose_name


class Goods(BaseModel):
    '''商品SPU模型类'''
    name = models.CharField(max_length=20, verbose_name='商品SPU名称')
    detail = HTMLField(blank=True, verbose_name='商品详情')  # 富文本
    
    # 在模型类中, 指定name为一种排序方式
    def OrderName(self):
        return self.name
    OrderName.admin_order_field = 'name'
    
    # 在模型类中, 指定列表为中文显示
    OrderName.short_description = "商品SPU模型类名称"

    # 管理类使用时, 返回的将是它的name, 而不是类名
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'df_goods'
        verbose_name = '商品SPU'
        verbose_name_plural = verbose_name
    

class GoodsImage(BaseModel):
    '''商品图片模型类'''
    sku = models.ForeignKey('GoodsSKU', verbose_name='商品', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='goods', verbose_name='图片路径')  # 使用分布式储存

    class Meta:
        db_table = 'df_goods_image'
        verbose_name = '商品图片'
        verbose_name_plural = verbose_name


class IndexGoodsBanner(BaseModel):
    '''首页轮播商品展示模型类'''
    sku = models.ForeignKey('GoodsSKU', verbose_name='商品', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='banner', verbose_name='图片')
    index = models.SmallIntegerField(default=0,   verbose_name='展示顺序')

    class Meta:
        db_table = 'df_index_banner'
        verbose_name = '首页轮播商品'
        verbose_name_plural = verbose_name


class IndexTypeGoodsBanner(BaseModel):
    '''首页分类商品展示模型类'''
    DISPLAY_TYPE_CHOICES = (
        (0, "标题"),
        (1, "图片")
    )

    type = models.ForeignKey('GoodsType', verbose_name='商品类型', on_delete=models.CASCADE)
    sku = models.ForeignKey('GoodsSKU',   verbose_name='商品SKU', on_delete=models.CASCADE)
    display_type = models.SmallIntegerField(default=1,verbose_name='展示类型', choices=DISPLAY_TYPE_CHOICES)
    index = models.SmallIntegerField(default=0, verbose_name='展示顺序')

    class Meta:
        db_table = 'df_index_type_goods'
        verbose_name = "主页分类展示商品"
        verbose_name_plural = verbose_name


class IndexPromotionBanner(BaseModel):
    '''首页促销活动模型类'''
    name = models.CharField(max_length=20, verbose_name='活动名称')
    url = models.URLField(verbose_name='活动链接')
    image = models.ImageField(upload_to='banner', verbose_name='活动图片')
    index = models.SmallIntegerField(default=0, verbose_name='展示顺序')

    class Meta:
        db_table = 'df_index_promotion'
        verbose_name = "主页促销活动"
        verbose_name_plural = verbose_name