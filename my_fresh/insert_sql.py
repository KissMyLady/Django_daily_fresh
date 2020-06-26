# 文件名: Django_today -> insert_sql
# 创建时间: 2020/6/25 19:51
# 文件名: Flask_Project_Code -> insert_areas
# 创建时间: 2020/6/6 16:48

from pymysql import *
import os, sys
import datetime

# 删除数据
# delete from study_flask_note where id >100;
'''
"INSERT INTO `ih_area_info`(`name`) VALUES ('东城区'),('西城区'),('朝阳区'),('海淀区'),('昌平区'),('丰台区'),('房山区'),('通州区'),('顺义区'),
('大兴区'),('怀柔区'),('平谷区'),('密云区'),('延庆区'),('石景山区');"
'''


def main():
	n = datetime.datetime.now()
	conn = connect(host='localhost',
	               port=3306,
	               database='daily_sql',
	               user='root',
	               password='YING123ZZ',
	               charset='utf8')
	
	cs1 = conn.cursor()
	try:
		# count = cs1.execute("INSERT INTO `ih_facility_info`(`name`) VALUES('无线网络'),('热水淋浴'),('空调'),('暖气'),('允许吸烟'),
		# ('饮水设备'),('牙具'),('香皂'),('拖鞋'),('手纸'),('毛巾'),('沐浴露、洗发露'),('冰箱'),('洗衣机'),('电梯'),('允许做饭'),('允许带宠物'),('允许聚会'),
		# ('门禁系统'),('停车位'),('有线网络'),('电视'),('浴缸');")
		
		# INSERT INTO "df_goods_type" VALUES ('1', '0', '新鲜水果');
		# INSERT INTO "df_goods_type" VALUES ('2', '0', '海鲜水产');
		# INSERT INTO "df_goods_type" VALUES ('3', '0', '猪羊牛肉');
		# INSERT INTO "df_goods_type" VALUES ('4', '0', '禽类蛋品');
		# INSERT INTO "df_goods_type" VALUES ('5', '0', '新鲜蔬菜');
		# INSERT INTO "df_goods_type" VALUES ('6', '0', '速冻食品');
		
		cs1.execute('INSERT INTO "df_goods_type" VALUES ("1", "0", "新鲜水果")')
		cs1.execute('INSERT INTO "df_goods_type" VALUES ("2", "0", "海鲜水产")')
		cs1.execute('INSERT INTO "df_goods_type" VALUES ("3", "0", "猪羊牛肉")')
		cs1.execute('INSERT INTO "df_goods_type" VALUES ("4", "0", "禽类蛋品")')
		cs1.execute('INSERT INTO "df_goods_type" VALUES ("5", "0", "新鲜蔬菜")')
		cs1.execute('INSERT INTO "df_goods_type" VALUES ("6", "0", "速冻食品")')

		conn.commit()
		cs1.close()
		conn.close()
		print("插入成功")
	except Exception as e:
		print(e)


if __name__ == '__main__':
	main()


