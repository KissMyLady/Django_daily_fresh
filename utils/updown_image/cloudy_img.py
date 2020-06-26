# 创建时间: 2020/6/21 15:08
# python开发者文档: https://developer.qiniu.com/kodo/sdk/1242/python
# 查看密匙:  https://portal.qiniu.com/user/key


def down_load_of_Binary(file_data):
	'''
	上传文件到七牛
	:param file_data: 要上传的文件数据
	:return:
	'''
	from qiniu import Auth, etag, put_data
	access_key = "LfXjXvG1e6vPXV2UFLfXrJ14u2vqONh----"
	secret_key = "MRL5Y67LWpl_9_pOUPa7Ot8OD9R2pR3----"
	
	q = Auth(access_key, secret_key)
	
	# 上传后保存的文件名 可以指明, 也可以不指明(计算结果值当作文件名)
	# key = 'my-python-logo.png'
	keys = None
	
	# 生成上传 Token，可以指定过期时间等
	token = q.upload_token('flask-ihome-python65', key=keys, expires=3600)
	
	# 要上传文件的本地路径
	ret, info = put_data(token, key=keys, data=file_data)
	if info.status_code == 200:
		# 返回文件名
		return ret.get("key")
	else:
		raise Exception("图片上传服务器失败")

'''
info: _ResponseInfo__response:                      info
<Response [200]>,
exception:None,
status_code:200,
text_body:{"hash":"FikUyrLA_3Oaf7XJfBFOCbbkgU5J",
"key":"FikUyrLA_3Oaf7XJfBFOCbbkgU5J"},
req_id:K7IAAAAk4lmMmhUW, x_log:X-Log
--------------------                                ret
{'hash': 'FikUyrLA_3Oaf7XJfBFOCbbkgU5J',
 'key':  'FikUyrLA_3Oaf7XJfBFOCbbkgU5J'}
'''

# 直接敲入 hash值即可查看图片:  http://qbg25zlw0.bkt.clouddn.com/FikUyrLA_3Oaf7XJfBFOCbbkgU5J


if __name__ == "__main__":
	localfile = r'H:\我的文档\cut_up\test文件.png'
	with open(localfile, "rb") as f:
		binary_img = f.read()
		down_load_of_Binary(binary_img)
