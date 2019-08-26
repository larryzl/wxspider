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

import hashlib
import http.cookiejar as cookielib
import json
import logging
import logging.config
import math
import os
import random
import re
import string
import time

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from selenium import webdriver

from app import config
from app.settings import WXSTATIC_ROOT, WXSTATIC_DIR
from web_admin.models import Wechat, Article
from web_admin.utils.spider.combined_url import WechatSogouCombinedUrl
from web_admin.utils.spider.const import agents
from web_admin.utils.spider.filecache import WechatCache
from web_admin.utils.spider.sogou_parse import BeautiHtml
from web_admin.utils.spider.tools import may_int

logger = logging.getLogger(__name__)
logging.getLogger('django')


class SogouSpider:
	__HOME_PAGE = 'https://weixin.sogou.com/'
	__COOKIE_FILE = os.path.join(os.path.join(WXSTATIC_ROOT, 'cookie'), 'cookie.file')

	def __init__(self):
		self._cache = WechatCache(config.cache_dir, 60 * 60)
		self.__session = self._cache.get(config.cache_session_name) if self._cache.get(
				config.cache_session_name) else requests.session()

		self.__cookie = self.__load_cookie()
		self.__ua = self.__get_ua()
		if not self.__cookie:
			logger.error('init: not found cookie')
			self.__browser_search(keyword='', btn_type=2)
		self.set_cookie()

	def set_cookie(self):
		"""设置cookie
		"""
		cookie_jar = cookielib.MozillaCookieJar()
		for cookie in self.__load_cookie():
			cookie_jar.set_cookie(cookielib.Cookie(version=0, name=cookie['name'], value=cookie['value'], port=None,
			                                       port_specified=False, domain=cookie['domain'],
			                                       domain_specified=False, domain_initial_dot=False,
			                                       path=cookie['path'], path_specified=True,
			                                       secure=cookie['secure'], expires=None, discard=True,
			                                       comment=None, comment_url=None, rest={'HttpOnly': None},
			                                       rfc2109=False))
		self.__session.cookies.update(cookie_jar)
		return True

	def update_cookie(self, **kwargs):
		"""
		:param c_type: a 文章 w 微信号
		:param kwargs:
		:return:
		"""
		c_type = kwargs.get('c_type', 'a')
		if c_type == 'a':
			os.remove(self.__COOKIE_FILE)
			self.__browser_search(keyword='北京', btn_type=1)
			return True

	def __browser_search(self, keyword, btn_type=1):
		"""
		通过浏览器搜索
		:param keyword: 关键词
		:param btn_type: 1 文章搜索 2 公众号搜索
		:return:
		"""

		browser = webdriver.Chrome()
		browser.get('https://weixin.sogou.com/')
		try:
			btn_class = 'swz2' if btn_type == 2 else 'swz'
			inputs = browser.find_element_by_id('query')
			inputs.send_keys(keyword)
			search_button = browser.find_element_by_class_name(btn_class)
			search_button.click()
			div_tag = browser.find_element_by_class_name('txt-box')
			a_tag = div_tag.find_element_by_tag_name('a')
			a_tag.click()
			# dump_cookie_data = {each_cookie['name']: each_cookie['value'] for each_cookie in browser.get_cookies()}
			cookies = browser.get_cookies()
			logger.debug("__browser_search:cookies:{}".format(cookies))
			self.__dump_cookie(cookies)
			browser.close()
			return True
		except Exception as e:
			logger.error(e)
			return False

	def __dump_cookie(self, c):
		"""
		将cookie 写入文件
		:param c:
		:return:
		"""

		try:
			with open(self.__COOKIE_FILE, 'w') as f:
				json.dump(c, f)
				return True
		except Exception as e:
			logger.error('__dump_cookie:', e)
			return False

	def __load_cookie(self):
		"""从文件读取cookie
		"""
		if not os.path.exists(self.__COOKIE_FILE):
			return False
		try:
			with open(self.__COOKIE_FILE, 'r') as f:
				c = json.load(f)
		except EOFError:
			return {}
		except Exception as e:
			logger.error(e)
			return False
		return c

	def __get(self, url, session=None, headers=None, referer=None, is_encode=True):
		""" 发起http get请求
		:param url:
		:param session:
		:param headers:
		:param referer:
		:return: response
		"""
		if not url.startswith('http'):
			logger.error("url地址错误，地址: {}".format(url))
			return None

		logger.debug('爬取url：%s' % url)
		if not session: session = requests.session()
		requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
		# 缺省header
		if headers is None: headers = {'Host': 'weixin.sogou.com', 'User-Agent': self.__ua, 'referer': referer,
		                               'Accept': 'text/html,application/xhtml+xml',
		                               'Accept-Encoding': 'gzip, deflate, br', 'Cache-Control': 'no-cache',}
		session.headers.update(headers)
		try:
			resp = session.get(url, verify=False)
			if is_encode:
				resp.encoding = 'utf-8'
			return resp
		except Exception as e:
			logger.error("爬取错误，地址:{} Exception: {}".format(url, e))
			return None

	def __format_url(self, url, referer, text, session):
		"""
		通过 搜狗url 获取微信临时url
		:param url:
		:param referer:
		:param text:
		:param session:
		:return:
		"""

		def _parse_url(url_path, pads_list):
			b = math.floor(random.random() * 100) + 1
			logger.error("__format_url:_parse_url: 获取随机数:{}".format(str(b)))
			a = url_path.find("url=")
			c = url_path.find("&k=")
			if a != -1 and c == -1:
				sum_num = 0
				for i in list(pads_list) + [a, b]:
					# logger.error("__format_url:_parse_url: i:{}".format(str(i)))
					sum_num += int(i)
				a = url_path[sum_num]
				logger.error("__format_url:_parse_url: a:{}".format(str(a)))

			return '{}&k={}&h={}'.format(url_path, may_int(b), may_int(a))

		if url.startswith('/link?url='):
			self.referer = referer
			url = 'https://weixin.sogou.com{}'.format(url)
			pads = re.findall(r'href\.substr\(a\+(\d+)\+parseInt\("(\d+)"\)\+b,1\)', text)

			url = _parse_url(url, pads[0] if pads else [])

			logger.error("__format_url: url: {}".format(url))

			resp = self.__get(url,
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

	def __format_search_url(self, keyword):
		host = self.__HOME_PAGE + "/weixin"

	def __crawl_articles(self, label_name, sg_url_list, crawl_max, is_search=False, session=None):
		"""
		根据sg_url_list信息爬取文章
		:param sg_url_list:  搜狗页面url
		:param max_crawl: 最大爬取文章数量
		:return:  article_info 文章详细信息列表
		"""
		article_info = []
		if session is None: session = requests.session()

		for url_item in sg_url_list:
			if len(url_item) != 2:
				continue
			url, referer = url_item
			resp = self.__get(url=url, referer=referer)
			if resp is None:
				break
			if resp.status_code != requests.codes.ok:
				logger.error("请求地址：{} , 返回错误代码：{}".format(url, resp.status_code))
				continue
			if "请输入验证码" in resp.text:
				logger.error("请求地址：{} , 返回错误1，跳到验证码页面".format(url))
				break
			logger.debug("请求地址：{}, 获取搜狗搜索页内容成功".format(url))

			if not is_search:
				logger.debug("开始解析搜狗热门页面")
				article_list = BeautiHtml.sogou_hot_article_list_parse(resp.text)
			else:
				logger.debug("开始解析搜狗搜索页面")
				article_list = BeautiHtml.sogou_search_keyword_parse(resp.text)

			if len(article_list) == 0:
				logger.error("解析搜狗页面错误，返回文章列表为空")
				break
			logger.debug('共有 {} 条文章内容准备进入解析'.format(len(article_list)))
			for _ in article_list:
				twpid = hashlib.md5(str(str(_['title']) + str(_['wechat_name'])).encode()).hexdigest()
				logger.debug('twpid: {}'.format(twpid))
				if Article.objects.filter(twpid=twpid).count():
					logger.debug("文章《{}》 已经存在，跳过".format(_['title']))
					continue

				_['label_name'] = label_name
				_['twpid'] = twpid
				if not is_search:
					article_info.append(_)
				else:
					logger.debug("格式化搜索页面 content_url字段")
					_['content_url'] = self.__format_url(url=_['content_url'], referer=url, text=resp.text,
					                                     session=session)
					logger.debug("微信临时地址为：>>%s<<" % _['content_url'])
					if _['content_url'] == '' or _['content_url'] is None:
						continue

					article_info.append(_)
					logger.debug('成功添加一个微信地址')
				if len(article_info) >= int(crawl_max):
					return article_info

	@staticmethod
	def __generate_random(length=30, end=None):
		"""生成随机数
		"""
		r = []
		for x in range(length):
			r.append(random.choice(string.ascii_letters))
		return "".join(r) + end

	@staticmethod
	def __get_ua():
		"""
		获取随机ua
		:return:
		"""
		ua = random.choice(agents)
		return ua

	@staticmethod
	def __generate_sogou_hot_url(label_name='pc_0'):
		"""
		返回搜狗页面url
		:param label_name:
		:return: str
		"""
		logger.debug("开始生成搜狗热门页面地址")
		for index in range(0, 16):
			if index == 0:
				if label_name == 'pc_0':
					yield ('https://weixin.sogou.com', '')
				else:
					yield ('https://weixin.sogou.com/pcindex/pc/{}/{}.html'.format(label_name, label_name),
					       'https://weixin.sogou.com')
			else:
				yield (
					'https://weixin.sogou.com/pcindex/pc/{}/{}.html'.format(label_name, index),
					'https://weixin.sogou.com')

	@staticmethod
	def __save_image(url, save_name=None, path="avatar"):
		"""保存图片
		:param url: 下载地址
		:param path: 保存目录
		:param save_name: 保存名称
		:return [状态0、1，存储名称]
		"""
		if save_name is None: save_name = "".join([random.choice(string.ascii_letters) for _ in range(30)]) + ".png"

		image_name = os.path.join(os.path.join(WXSTATIC_ROOT, path), save_name)
		try:
			image = requests.get(url)
			logger.debug("下载图片成功: %s" % image_name)
		except Exception as e:
			logger.debug("下载图片失败: %s" % image_name)
			return [1, '']
		with open(image_name, 'wb') as f:
			f.write(image.content)
		return [0, save_name]

	def __mp_header(self, referer=None):
		"""
		获取微信header
		:param referer:
		:return:
		"""
		if referer is None:
			referer = 'weixin.sogou.com'

		headers = {
			'Host': 'mp.weixin.qq.com',
			'User-Agent': self.__get_ua(),
			'referer': referer
		}
		return headers

	def search_gzh(self, keyword, page=1, decode_url=True, is_save_image=True):
		"""搜索公众号
		:param is_save_image:
		:param decode_url:
		:param keyword: 名称 or ID
		:param page: 页码
		"""

		session = self.__session

		# logger.error("1 Create Session: {}".format(session))
		url = next(WechatSogouCombinedUrl.search_url(keyword))
		# logger.error("2. combined url: %s" % url)
		resp = self.__get(url)
		if resp is None:
			return None
		if resp.status_code == requests.codes.ok:

			if "请输入验证码" in resp.text:
				# logger.error("返回错误1，跳到验证码页面")
				return None

			# logger.error("3. get response success")
			gzh_list = BeautiHtml.gzh_parse(resp.text)
			for i in gzh_list:
				if decode_url:
					# logger.error("4. update profile_url")
					i['profile_url'] = self.__format_url(url=i['profile_url'], referer=url, text=resp.text,
					                                     session=session)
					# logger.error("5. new profile_url：{}".format(i['profile_url']))
					if is_save_image:
						img_url = "http:" + i['headimage']
						qrcode_url = i['qrcode']
						self.__save_image(url=img_url)
						self.__save_image(qrcode_url, save_name=img_url.split('/')[-1] + "_qrcode.png")
				yield i
		else:
			logger.error(resp.code)

	def get_gzh_info(self, wechat_id, decode_url=True):
		"""
		通过 公众号名称或ID 获取公众号信息

		:param wechat_id: 公众号 名称 或 ID
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
			info = next(self.search_gzh(wechat_id, 1, decode_url))
			# logger.error("get_gzh_info info: ", info)
			return info
		except StopIteration:
			return None

	def crawl_wechat_articles(self, article_info_list, is_save_img=True):
		"""爬取微信文章信息
		:param is_save_img: 存储图片
		:param article_info_list: 文章信息表
		--------
		article_url_list:
			[
				{
				'cover_url': str 文章缩略图
				'title': str, 文章标题
				'content_url': str, 文章临时url
				"description": str, 文章描述
				"date_time": str, 文章时间
				"wechat_avatar": str, 公众号头像
				"wechat_profile_url": str,  公众号地址
				"wechat_name": str 公众号名称
				"label": str 文章分类标签
				}
			]
		article_detail:
		{
			"title": title                  # 文章标题
			"source_url": source_url,       # 原文地址
			"author": author,               # 作者
			"wechat_name": wechat_name,     # 公众号名称
			"wechat_id": wechat_id,         # 公众号ID
			"wechat_desc": wechat_desc,     # 公众号描述
			"msg_index": msg_index,         # 消息序号 int
			"copyright_stat": copyright_stat,# 是否原创 0 为原创，1非原创
			"content": str(content),        # 文章内容
			"qrcode":qrcode,                # 二维码地址
			"publish_time": publish_time    # 发布时间
		}
		--------
		:return list
		[
			{
			'cover_url': str                # 文章缩略图
			'title': str,                   # 文章标题
			'content_url': str,             # 文章临时url
			"description": str,             # 文章描述
			"date_time": str,               # 文章时间
			"wechat_avatar": str,           # 公众号头像
			"wechat_profile_url": str,      # 公众号地址
			"label": str                    # 文章分类标签
			"source_url": source_url,       # 原文地址
			"author": author,               # 作者
			"wechat_name": wechat_name,     # 公众号名称
			"wechat_id": wechat_id,         # 公众号ID
			"wechat_desc": wechat_desc,     # 公众号描述
			"msg_index": msg_index,         # 消息序号 int
			"copyright_stat": copyright_stat,# 是否原创 0 为原创，1非原创
			"content": str(content),        # 文章内容
			"qrcode":qrcode,                # 二维码地址
			"publish_time": publish_time    # 发布时间
			}
		]
		"""
		if not isinstance(article_info_list, list):
			return False
		logger.debug("开始抓取微信文章页面，共抓取 {} 篇文章".format(len(article_info_list)))
		articles_info = []
		# 计数器

		for item in article_info_list:
			if not isinstance(item, dict):
				continue
			else:
				item = {str(k): str(v) for k, v in item.items()}

			resp = self.__get(item['content_url'], headers=self.__mp_header())
			if resp is None:
				logger.error("抓取微信文章页面错误, 文章地址: {}".format(item['content_url']))
				continue
			# 判断是否返回正常代码
			if resp.status_code != requests.codes.ok:
				logger.error("抓取微信文章页面错误,网页代码: {} , 文章地址: {}".format(resp.status_code, item['content_url']))
				continue
			# 开始解析微信文章内容
			article_detail = BeautiHtml.wechat_article_detail_parse(resp.text)
			if article_detail is None:
				continue
			if article_detail['wechat_id'] is None or article_detail['wechat_id'] == '':
				continue
			item.update(article_detail)

			# 存储图片
			if is_save_img:
				# 存储文章缩略图
				_, name = self.__save_image(url=item['cover_url'], save_name=None, path='article')
				if _ == 0:
					item['cover_url'] = WXSTATIC_DIR + 'article/' + name
				# 判断是否需要存储公众号图片
				if not Wechat.objects.filter(wechatid=item['wechat_id']).count():
					if 'wechat_avatar' in item.keys():
						_, name = self.__save_image(url=item['wechat_avatar'], path='avatar')
						if _ == 0: item['wechat_avatar'] = WXSTATIC_DIR + 'avatar/' + name
					if 'qrcode' in item.keys():
						_, name = self.__save_image(url=item['qrcode'], path='avatar')
						if _ == 0: item['qcode'] = WXSTATIC_DIR + 'avatar/' + name
			articles_info.append(item)
			time.sleep(random.random() * 2)
		return articles_info

	def crawl_hotpage_articles(self, crawl_max=1, label_name='pc_0'):
		"""
		抓取搜狗热门文章
		:param label_name: 热门类型
		:param crawl_max: 最大抓取数量
		:return: list[dict]
		"""
		logger.debug("开始抓取搜狗热门文章,爬取数量:{},爬取标签:{}".format(crawl_max, label_name))

		url_list = self.__generate_sogou_hot_url(label_name=label_name)

		article_info = self.__crawl_articles(label_name=label_name, sg_url_list=url_list, crawl_max=crawl_max,
		                                     is_search=False)

		return self.crawl_wechat_articles(article_info_list=article_info)

	def crawl_keyword_articles(self, crawl_max, keyword, crawl_url=None):
		"""
		根据关键词获取文章
		:param crawl_max: 爬取文章数量
		:param keyword:  爬取关键字
		:param crawl_url:  指定爬取地址
		:param kwargs:
		:return: list[dict]
		"""
		logger.debug('开始抓取关键字文章，抓取文章数:{}'.format(crawl_max))

		session = self.__session
		url_list = [crawl_url] if crawl_url is not None else WechatSogouCombinedUrl.search_url(keyword=keyword, type=2)

		article_info = self.__crawl_articles(label_name='pc_0', sg_url_list=url_list, crawl_max=crawl_max,
		                                     is_search=True, session=session)

		return self.crawl_wechat_articles(article_info_list=article_info)

	def update_wechat_article_kind(self, url=None):
		"""更新微信文章分类，及标签
		:param url:
		"""

		if url is None: url = "https://weixin.sogou.com/"
		sogou_resp = self.__get(url)
		if sogou_resp.status_code == requests.codes.ok:
			logger.error("获取搜狗首页内容成功")
			kind_list = BeautiHtml.sogou_article_label_parse(sogou_resp.text)
			return kind_list
		else:
			return []

	def update_sogou_hotword(self, url=None):
		"""更新搜狗热词
		:param url:
		"""
		if url is None: url = "https://weixin.sogou.com/"
		sogou_resp = self.__get(url)
		if sogou_resp.status_code == requests.codes.ok:
			logger.debug("获取搜狗首页内容成功")
			hotword_list = BeautiHtml.sogou_hotword(sogou_resp.text)
			return hotword_list
		else:
			return []

	def update_weibo_hotword(self, url=None):
		"""更新搜狗热词
		:param url:
		"""
		headers = {'Host': 's.weibo.com', 'User-Agent': self.__ua,
		           'Accept': 'text/html,application/xhtml+xml',
		           'Accept-Encoding': 'gzip, deflate, br', 'Cache-Control': 'no-cache',}
		if url is None: url = "https://s.weibo.com/top/summary?Refer=top_ho"
		resp = self.__get(url, referer='https://weibo.com', session=requests.session(), headers=headers)
		if resp.status_code == requests.codes.ok:
			logger.debug("获取微博热搜页内容成功")
			hotword_list = BeautiHtml.weibo_tophot_parse(resp.text)

			return hotword_list
		else:
			return []
