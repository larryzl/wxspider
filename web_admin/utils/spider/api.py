#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/1 10:57 AM
@Author  : Larry
@Site    : 
@File    : api.py
@Software: PyCharm
@Desc    :

"""
import requests
import re

from selenium import webdriver

from urllib.parse import urlencode
import requests
import random
import math
from web_admin.utils.spider.tools import may_int
from web_admin.utils.spider.sogou_parse import BeautiHtml
from web_admin.utils.spider.combined_url import WechatSogouCombinedUrl
from web_admin.utils.spider.identify_img import identify_image_callback_by_hand
from web_admin.utils.spider.const import agents, CookieSpool


class SogouSpider:

	__base_url = 'https://weixin.sogou.com/weixin?'
	__referer = 'https://weixin.sogou.com/'

	def __init__(self,captcha_break_times=2):

		self.captcha_break_times = captcha_break_times

	@property
	def __referer(self):
		return self.__referer

	@__referer.setter
	def __referer(self, value):
		self.__referer = value

	def __set_cookie(self, suv=None, suid=None):
		if suv is None and suid is None:
			cookie = CookieSpool.pop()
		else:
			cookie = {
				'SUV': suv,
				'SUID': suid
			}
		return cookie

	def __format_url(self, url, referer, text, unlock_callback=None, identify_image_callback=None, session=None):
		def _parse_url(url, pads):
			b = math.floor(random.random() * 100) + 1
			a = url.find("url=")
			c = url.find("&k=")
			if a != -1 and c == -1:
				sum = 0
				for i in list(pads) + [a, b]:
					sum += int(i)
				a = url[sum]
			return '{}&k={}&h={}'.format(url, may_int(b), may_int(a))
		if url.startswith('/link?url='):
			url = 'https://weixin.sogou.com{}'.format(url)

			pads = re.findall(r'href\.substr\(a\+(\d+)\+parseInt\("(\d+)"\)\+b,1\)', text)
			url = _parse_url(url, pads[0] if pads else [])
			resp = self.__get_by_unlock(url,
			                            referer=referer,
			                            unlock_platform=None,
			                            unlock_callback=unlock_callback,
			                            identify_image_callback=identify_image_callback,
			                            session=session)
			uri = ''
			base_url = re.findall(r'var url = \'(.*?)\';', resp.text)
			if base_url and len(base_url) > 0:
				uri = base_url[0]

			mp_url = re.findall(r'url \+= \'(.*?)\';', resp.text)
			if mp_url:
				uri = uri + ''.join(mp_url)
			url = uri.replace('@', '')
		return url

	def headers(self):
		"""
		获取header
		:return: dict
		"""
		header = {
			'Cookie': self.__set_cookie(),
			'Host': 'weixin.sogou.com',
			'referer': self.__referer
		}
		ua = agents[random.randint(0, len(agents) - 1)]
		header['User-Agent'] = ua
		return header

	def __get(self, url, session, headers=None, **kwargs):
		h = self.headers() if self.headers() else headers
		resp = session.get(url, headers=h, **kwargs)
		if not resp.ok:
			raise ('WechatSogouAPI get error', resp)
		else:
			return resp

	def __get_by_unlock(self, url, referer=None, unlock_platform=None, unlock_callback=None,
	                    identify_image_callback=None, session=None):
		assert unlock_platform is None or callable(unlock_platform)

		if identify_image_callback is None:
			identify_image_callback = identify_image_callback_by_hand
		assert unlock_callback is None or callable(unlock_callback)
		assert callable(identify_image_callback)

		if not session:
			session = requests.session()
		resp = self.__get(url, session, headers=self.headers())

		resp.encoding = 'utf-8'
		if 'antispider' in resp.url or '请输入验证码' in resp.text:
			for i in range(self.captcha_break_times):
				try:
					unlock_platform(url=url, resp=resp, session=session, unlock_callback=unlock_callback,
					                identify_image_callback=identify_image_callback)
					break
				except:
					if i == self.captcha_break_times - 1:
						raise "验证失败"

			if '请输入验证码' in resp.text:
				resp = session.get(url)
				resp.encoding = 'utf-8'
			else:
				headers = self.__set_cookie(referer=referer)
				headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64)'
				resp = self.__get(url, session, headers)
				resp.encoding = 'utf-8'

		return resp

	def search_gzh(self, keyword, page=1, unlock_callback=None, identify_image_callback=None, decode_url=True):
		"""
		搜索公众号
		:param keyword: 搜索文字
		:param page: 页码
		:param unlock_callback: 处理出现验证码页面的函数
		:param identify_image_callback: 处理验证码函数
		:param decode_url: 是否解析url
		:return:
        list[dict]
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

        Raises
        ------
        WechatSogouRequestsException
            requests error

		"""

		url = WechatSogouCombinedUrl.gzh_search_url(keyword, page)
		session = requests.session()
		resp = self.__get_by_unlock(url,session=session)
		gzh_list =  BeautiHtml.gzh_parse(resp.text)
		for i in gzh_list:
			if decode_url:
				i['profile_url'] = self.__format_url(i['profile_url'], url, resp.text, unlock_callback=unlock_callback, identify_image_callback=identify_image_callback, session=session)
			yield i

	def get_gzh_info(self, wecgat_id_or_name, unlock_callback=None, identify_image_callback=None, decode_url=True):
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
		try:
			return next(self.search_gzh(wecgat_id_or_name, 1, unlock_callback, identify_image_callback, decode_url))
		except StopIteration:
			return None
