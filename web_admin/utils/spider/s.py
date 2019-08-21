#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/8 11:47 AM
@Author  : Larry
@Site    : 
@File    : s.py
@Software: PyCharm
@Desc    :

"""

import wechatsogou

import requests
import pickle
import random
import re
import os
from app.settings import WXSTATIC_ROOT
import math
from selenium import webdriver
from web_admin.utils.spider.tools import may_int
from web_admin.utils.spider.sogou_parse import BeautiHtml
from web_admin.utils.spider.combined_url import WechatSogouCombinedUrl
from web_admin.utils.spider.const import agents


class SogouSpider:
	_home_page = 'https://weixin.sogou.com/'
	_cookie_file = 'cookie.file'
	_ua_file = 'ua.file'

	def __init__(self):
		self._cookie = self._load_cookie()
		if self._cookie is None:
			self._dump_cookie(self._browser_search('北京'))
		self._dump_ua()

	def _browser_search(self, keyword, btn_type=1):
		"""
		通过浏览器搜索
		:param keyword: 关键词
		:param btn_type: 1 文章搜索 2 公众号搜索
		:return:
		"""
		btn_class = 'swz2' if btn_type == 2 else 'swz'
		browser = webdriver.Chrome()
		browser.get(self._home_page)
		input_str = browser.find_element_by_id('query')
		input_str.send_keys(keyword)
		button = browser.find_element_by_class_name(btn_class)
		button.click()
		suid = browser.get_cookie('SUID').get('value')
		suv = browser.get_cookie('SUV').get('value')
		snuid = browser.get_cookie('SNUID').get('value')
		browser.close()
		return {'SUID': suid, 'SUV': suv, 'SNUID': snuid}

	def _dump_cookie(self, c):
		"""
		将cookie 写入文件
		:param c:
		:return:
		"""

		try:
			with open(self._cookie_file, 'wb') as f:
				pickle.dump(c, f, 0)
				return True
		except Exception as e:
			print(e)
			return False

	def _load_cookie(self):
		"""从文件读取cookie
		"""
		with open(self._cookie_file, 'rb') as f:
			c = pickle.load(f)
		return c

	def _load_ua(self):
		with open(self._ua_file, 'rb') as f:
			return pickle.load(f)

	def _dump_ua(self):
		ua = agents[random.randint(0, len(agents) - 1)]
		with open(self._ua_file, 'wb') as f:
			pickle.dump(ua, f, 0)

	def _get(self, url, session=None, headers=None, referer=None,is_encode=True):
		""" 发起http get请求
		:param url:
		:param session:
		:param headers:
		:param referer:
		:return:
		"""
		session = requests.session() if not session else session
		if headers is None:
			headers = {
				'Cookie': str(self._cookie),
				'Host': 'weixin.sogou.com',
				'User-Agent': self._load_ua(),
				'referer': referer
			}
		resp = session.get(url, headers=headers, cookies=self._cookie)
		if is_encode:
			resp.encoding = 'utf-8'
		return resp

	def _format_url(self, url, referer, text, session):
		def _parse_url(url_path, pads_list):
			b = math.floor(random.random() * 100) + 1
			a = url_path.find("url=")
			c = url_path.find("&k=")
			if a != -1 and c == -1:
				sum_num = 0
				for i in list(pads_list) + [a, b]:
					sum_num += int(i)
				a = url_path[sum_num]
			return '{}&k={}&h={}'.format(url_path, may_int(b), may_int(a))

		if url.startswith('/link?url='):
			self.referer = referer
			url = 'https://weixin.sogou.com{}'.format(url)

			pads = re.findall(r'href\.substr\(a\+(\d+)\+parseInt\("(\d+)"\)\+b,1\)', text)
			url = _parse_url(url, pads[0] if pads else [])
			resp = self._get(url,
			                 referer=referer,
			                 session=session)
			uri = ''
			base_url = re.findall(r'var url = \'(.*?)\';', resp.text)
			if base_url and len(base_url) > 0:
				uri = base_url[0]

			mp_url = re.findall(r'url \+= \'(.*?)\';', resp.text)
			if mp_url:
				uri += ''.join(mp_url)
			url = uri.replace('@', '')
		return url

	def search_gzh(self, keyword, page=1, decode_url=True,is_save_image=True):
		"""搜索公众号
		:param is_save_image:
		:param decode_url:
		:param keyword: 名称 or ID
		:param page: 页码
		"""
		session = requests.session()

		url = WechatSogouCombinedUrl.search_url(keyword, page)
		resp = self._get(url, session, referer=self._home_page)
		if resp.ok:
			gzh_list = BeautiHtml.gzh_parse(resp.text)
			for i in gzh_list:
				if decode_url:
					i['profile_url'] = self._format_url(url=i['profile_url'], referer=url, text=resp.text,
					                                    session=session)
					if is_save_image:
						img_url = "http:"+i['headimage']
						self.save_image(url=img_url)
				yield i
		else:
			print(resp.code)

	def get_gzh_info(self, wecgat_id_or_name, decode_url=True):
		"""
		通过 公众号名称或ID 获取公众号信息

		:param wecgat_id_or_name: 公众号 名称 或 ID
		:param unlock_callback: 处理出现验证码页面的方法
		:param identify_image_callback: 处理验证码函数
		:param decode_url:
		:return
        dict or None
            {
                'open_id': '', # 微信号唯一ID
                'profile_url': '',  # 最近10条群发页链接
                'headimage': '',  # 头像
                'wechat_name': '',  # 名称
                'wechat_id': '',  # 微信id
                'post_perm': '',  # 最近一月群发数
                'qrcode': '',  # 二维码
                'introduction': '',  # 介绍
                'authentication': ''  # 认证
            }
		"""
		info = next(self.search_gzh(wecgat_id_or_name, 1, decode_url))
		try:
			return info
		except StopIteration:
			return None

	@staticmethod
	def save_image(url):
		try:
			image_name = os.path.join(WXSTATIC_ROOT, url.split('/')[-1] + ".png")
			image = requests.get(url)
		except requests.exceptions.ConnectionError:
			return [1, '下载失败']
		with open(image_name, 'wb') as f:
			f.write(image.content)
		return [0, url.split('/')[-1] + ".png"]


if __name__ == '__main__':
	s = SogouSpider()

	print(s.get_gzh_info('北京'))
