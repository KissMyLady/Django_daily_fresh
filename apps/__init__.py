# 文件名: Django_today -> __init__.py
# 创建时间: 2020/6/21 0:48
import os
a = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
b = os.path.dirname(os.path.abspath(__file__))
print(a)  # D:\Django_today\my_fresh
print(b)