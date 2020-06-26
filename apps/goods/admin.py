from django.contrib import admin
from goods.models import GoodsType             # 商品类型模型类
from goods.models import IndexGoodsBanner      # 首页轮播商品展示模型类
from goods.models import IndexTypeGoodsBanner  # 首页分类商品展示模型类
from goods.models import IndexPromotionBanner  # 首页活动促销模型类
from goods.models import Goods
from goods.models import GoodsSKU
from django.core.cache import cache


# 基础继承类, 每次行新增或删除文件后, 重新刷新缓存index文件 使用celery异步执行
# windows不支持celery, 这里选择暂时注释
class BaseModelAdmin(admin.ModelAdmin):
	def save_model(self, request, obj, form, change):
		'''新增或更新表中的数据时调用'''
		super().save_model(request, obj, form, change)

		# 发出任务，让celery worker重新生成首页静态页
		# from celery_tasks import generate_static_index_html
		# generate_static_index_html.delay()

		# 清除首页的缓存数据
		# cache.delete('index_page_data')

	def delete_model(self, request, obj):
		'''删除表中的数据时调用'''
		super().delete_model(request, obj)
		# 发出任务，让celery worker重新生成首页静态页
		# from celery_tasks.tasks import generate_static_index_html
		# generate_static_index_html.delay()

		# 清除首页的缓存数据
		# cache.delete('index_page_data')


# 富文本编辑器的使用
class GoodsTypeAdmin(BaseModelAdmin):
	pass


class IndexGoodsBannerAdmin(BaseModelAdmin):
	pass


class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
	pass


class IndexPromotionBannerAdmin(BaseModelAdmin):
	pass


class GoodsSKUAdmin(BaseModelAdmin):
	list_per_page = 30  # 每个管理页面显示30条
	# id, 商品种类, 名字, 单位, 价格, 库存, 状态
	list_display = ['id', 'type', 'name', 'unite', 'price', 'stock', 'sales', 'status']


class GoodsInfoAdmin(admin.ModelAdmin):
	list_per_page = 20
	list_display = ['id', 'name', 'detail']  # 表格列, 将要显示什么
	# 管理类, 对名字name进行排序
	# 见goods模型类def的定义
	

admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(Goods, GoodsInfoAdmin)
admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
