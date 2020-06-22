from django.test import TestCase
# Create your tests here.
import sys


def pinrt_code_line():
	# 输出当前行号
	print(sys._getframe().f_lineno)
	

def Secert():
	from itsdangerous import TimedJSONWebSignatureSerializer as safe
	
	safe_obj = safe('This is my secretkey', 360)
	infomations = {'confirm': 1,
	               'nums': 66,
	               'images': "肖像",
	               'money': "milenr" }
	
	# 加密
	response = safe_obj.dumps(infomations)
	print(response)
	
	# 解密
	re_load = safe_obj.loads(response)
	print(re_load) # {'confirm': 1, 'nums': 66, 'images': '肖像', 'money': 'milenr'}
	
	
if __name__ == '__main__':
	Secert()