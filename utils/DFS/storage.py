#
# 描述: DFS有点难搞, 先使用云平台凑合
#
from django.core.files.storage import Storage
from django.conf import settings
from updown_image.cloudy_img import down_load_of_Binary  # 云平台
from Logging import Use_Loggin


class FDFSStorage(Storage):
    def __init__(self):
        self.logging = Use_Loggin()

    def _open(self, name, mode='rb'):
        '''打开文件时使用'''
        pass

    def _save(self, name, content):
        '''保存文件时使用'''
        # 上传文件到云平台中
        try:
            image_file_name = down_load_of_Binary(content.read())
        except:
            self.logging.error("第三方保存图片错误")
            raise Exception('上传文件到第三方失败')
        
        # 获取返回的文件ID
        return image_file_name

    def exists(self, name):
        '''Django判断文件名是否可用'''
        return False

    def url(self, name):
        '''返回访问文件的url路径'''
        from django.conf import settings
        return settings.CLOUDY_IMG_URL_PREFIX + name



