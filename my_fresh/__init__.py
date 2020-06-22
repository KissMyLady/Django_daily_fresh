import pymysql

pymysql.install_as_MySQLdb()


# 初始化时, base.py第35, 36行需要注释, 版本问题
# operations.py文件的第146行, 把decode改成encode