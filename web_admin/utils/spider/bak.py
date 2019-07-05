#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/26 2:07 PM
@Author  : Larry
@Site    : 
@File    : wxspider.py
@Software: PyCharm
@Desc    :

"""

import wechatsogou
import requests
from app.settings import WXSTATIC_ROOT
import os
from hashlib import md5
from wechatsogou import WechatSogouAPI, WechatSogouConst


class Sgspider:
	ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=3)

	# def __init__(self,captcha_break_time=3):
	# 	"""
	# 	:param captcha_break_time:  设置超时时间
	# 	:return:
	# 	"""
	# 	self.ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=captcha_break_time)

	@classmethod
	def get_gzh_info(cls, wecgat_id_or_name, **kwargs):
		"""
		获取特定公众号信息
		:param wecgat_id_or_name:  公众号 名称或ID
		:param kwargs:
		:return:
		"""
		return cls.ws_api.get_gzh_info(wecgat_id_or_name, identify_image_callback=cls.identify_image_callback_sogou,
		                               **kwargs)

	@classmethod
	def search_gzh(cls, keyword, **kwargs):
		"""
		搜索公众号
		:param keyword: 关键词
		:return:
		"""
		return cls.ws_api.search_gzh(keyword, **kwargs)

	@classmethod
	def search_article(cls, keyword, **kwargs):
		"""
		搜索文章
		:param keyword: 关键词
		:param kwargs:
		:return:
		"""

		return cls.ws_api.search_article(keyword, **kwargs)

	@classmethod
	def get_gzh_article_by_history(cls, keyword, **kwargs):
		"""
		解析最近文章
		:param keyword:
		:param kwargs:
		:return:
		"""
		return cls.ws_api.get_gzh_article_by_history(keyword, **kwargs)

	def identify_image_callback(self):
		"""

		:return:
		"""
		pass

	@classmethod
	def test_get_article_content(cls):
		k = '北京'
		gzh_article = cls.ws_api.get_gzh_article_by_history(k,
		                                                    identify_image_callback_sogou=cls.identify_image_callback_ruokuai_sogou,
		                                                    identify_image_callback_weixin=cls.identify_image_callback_ruokuai_weixin)
		print(gzh_article)

	@classmethod
	def __identify_image_callback(cls, img, code):
		import os
		try:
			username = os.environ['rk_username']
			password = os.environ['rk_password']
			id_ = os.environ['rk_id']
			key = os.environ['rk_key']

		except Exception:
			raise Exception('识别验证码错误')

	@classmethod
	def identify_image_callback_ruokuai_sogou(cls, img):
		return cls.__identify_image_callback(img, 3060)

	@classmethod
	def identify_image_callback_ruokuai_weixin(cls, img):
		return cls.__identify_image_callback(img, 3040)

	@staticmethod
	def readimg(content):
		import tempfile
		from PIL import Image
		f = tempfile.TemporaryFile()
		f.write(content)
		return Image.open(f)

	@classmethod
	def identify_image_callback_sogou(cls, img):

		im = cls.readimg(img)

		im.save(os.path.join(WXSTATIC_ROOT, 'code.png'), format='PNG')

		return input("please input code: ")

	@staticmethod
	def save_image(path):
		try:
			image_name = os.path.join(WXSTATIC_ROOT, path.split('/')[-1] + ".png")
			image = requests.get(path, timeout=5)
		except requests.exceptions.ConnectionError:
			return [1, '下载失败']
		with open(image_name, 'wb') as f:
			f.write(image.content)
		return [0, path.split('/')[-1] + ".png"]


if __name__ == "__main__":
	# print(Sgspider.get_gzh_info('天使宝宝攻略'))
	print(Sgspider.save_image("https://img01.sogoucdn.com/app/a/100520090/oIWsFt24IbHmZjoV7rk_pJdQ3xmU"))
# sg.get_gzh_article_by_hot()
