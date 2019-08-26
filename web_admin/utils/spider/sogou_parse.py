#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/4 5:10 PM
@Author  : Larry
@Site    : 
@File    : sogou_parse.py
@Software: PyCharm
@Desc    :

"""

import datetime
import logging
import logging.config
import re

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logging.getLogger('django')


class BeautiHtml:
	def __init__(self):
		pass

	@classmethod
	def gzh_parse(cls, html):
		gzh_info = []
		soup = BeautifulSoup(html, 'lxml')
		for es in soup.find_all(class_='news-list2'):
			for li in es.find_all('li'):
				# 微信号唯一ID
				open_id = li['d']
				# 服务号名称
				wechat_name = "".join([str(x) for x in li.find_all(class_='txt-box')[0].a.contents]).replace(
						'<!--red_end--></em>', '').replace('<em><!--red_beg-->', '')
				# 服务号ID
				wechat_id = str(li.label.string)
				# 服务号临时地址
				profile_url = li.find_all(class_='tit')[0].a['href']
				# 头像
				headimage = li.div.div.a.img['src']
				# 二维码
				qrcode = li.find_all(class_='ew-pop')[0].span.img['src']
				# 简介
				introduction = "".join([str(x) for x in li.dl.dd.contents]).replace(
						'<!--red_end--></em>', '').replace('<em><!--red_beg-->', '')
				# 认证
				try:
					authentication = str(li.find_all('dl')[1].dd.contents[-1])
				except:
					authentication = ''

				gzh_info.append({
					'open_id': open_id,
					'profile_url': profile_url,
					'headimage': headimage,
					'wechat_name': wechat_name.replace('red_beg', '').replace('red_end', ''),
					'wechat_id': wechat_id,
					'qrcode': qrcode,
					'introduction': introduction.replace('red_beg', '').replace('red_end', ''),
					'authentication': authentication,
					'post_perm': -1,
					'view_perm': -1,
				})
		return gzh_info

	@classmethod
	def sogou_hot_article_list_parse(cls, html):
		"""搜狗热门页解析
		:param html:
		:return
		------
		'cover_url': conver_url,                    # 文章封面图
		'title': title,                             # 文章标题
		'content_url': content_url,                 # 文章临时url
		"description": description,                 # 文章描述
		"date_time": date_time,                     # 文章时间
		"wechat_avatar": wechat_avatar,             # 公众号头像
		"wechat_profile_url": wechat_profile_url,   # 公众号临时地址
		"wechat_name": wechat_name                  # 公众号名称
		------

		"""
		article_list = []
		soup = BeautifulSoup(html, 'lxml')

		try:
			article_parse = soup.find(class_="news-list").find_all('li')
		except:
			article_parse = soup.find_all('li')

		for _ in article_parse:
			if _ is None: continue
			if _.find(attrs={"class": "img-box"}) is None: continue
			try:
				description = _.find(class_="txt-box").p.string
				title = _.find(class_="txt-box").a.string
				wechat_name = _.find(class_='s-p').a.string
				conver_url = "http:" + _.find(attrs={"class": "img-box"}).a.img['src']
				wechat_avatar = "http:" + _.find(class_='s-p').a['data-headimage']
				content_url = _.find(class_="txt-box").a['href']
				date_time = _.find(class_="s2")['t']
				wechat_profile_url = _.find(class_='s-p').a['href']
			except:
				continue
			data = {'cover_url': conver_url, 'title': title, 'content_url': content_url, "description": description,
			        'date_time': date_time, 'wechat_avatar': wechat_avatar, "wechat_profile_url": wechat_profile_url,
			        "wechat_name": wechat_name}
			article_list.append(data)

		logger.debug("解析搜狗热门页完成，共解析%s 条文章" % len(article_list))
		return article_list

	@classmethod
	def wechat_article_detail_parse(cls, html):
		""" 微信文章页字段解析

		:param html:
		:return: dict
		-------
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
		-------
		"""
		logger.debug("开始解析微信文章页面")

		def __format_item(text):
			"""
			替换换行符
			"""
			if text is None:
				return ''
			return text.replace("\n", "").lstrip().rstrip()

		soup = BeautifulSoup(html, 'lxml')
		# 原文地址
		try:
			source_url = soup.find(attrs={"id": "js_sg_bar"}).a['href']
		except Exception:
			source_url = ""
		# 作者
		try:
			author = __format_item(soup.find(attrs={"id": "meta_content"}).span.string)
		except:
			author = ''

		try:
			title = __format_item(soup.find(attrs={'id': 'activity-name'}).string)
			wechat_name = __format_item(soup.find(attrs={"id": "js_name"}).string)

			# 公众号ID、描述
			wechat_id, wechat_desc = [__format_item(x.string) for x in
			                          soup.find(attrs={"id": "js_profile_qrcode"}).find_all(
				                          class_="profile_meta_value")]
			# 群发ID
			msg_index = 1
			publish_time = datetime.datetime.now()
			qrcode = ''
			for i in soup.find_all('script'):
				if "var idx = " in i.string:
					try:
						msg_index = str(re.findall('var idx = .* \"(\d+)\"', i.string)[0])
					# logger.error("解析发文顺序为:%s" % msg_index)
					except:
						pass
				if "var ct =" in i.string:
					try:
						publish_time = str(re.findall('var ct = .*\"(\d+)\"', i.string)[0])
						publish_time = str(datetime.datetime.fromtimestamp(float(publish_time)))
					except Exception as e:
						pass
				if "window.sg_qr_code" in i.string:
					try:
						qrcode = str(re.findall('window.sg_qr_code="(.+)";', i.string)[0])
						qrcode = 'https://mp.weixin.qq.com' + qrcode.replace('\\x26amp;', '&')
					except Exception as e:
						pass

			# 是否为原创
			copyright_stat = 1 if soup.find(attrs={"id": "copyright_stat"}) else 0
			# logger.error("解析原创为:%s" % copyright_stat)
			content = str(soup.find(attrs={"id": "js_content"}))
			# logger.error("解析内容为：%s" % content)
			logger.debug("解析微信文章页面完成")
			return {
				"title": title,
				"source_url": source_url,
				"author": author,
				"wechat_name": wechat_name,
				"wechat_id": wechat_id,
				"wechat_desc": wechat_desc,
				"msg_index": msg_index,
				"copyright_stat": copyright_stat,
				"content": content,
				"qrcode": qrcode,
				"publish_time": publish_time
			}
		except:
			logger.error("解析微信文章页面失败")
			return None

	@classmethod
	def sogou_article_label_parse(cls, html):
		"""
		搜狗标签解析
		:param html:
		:return: dict
		"""

		logger.debug("开始解析文章分类")
		soup = BeautifulSoup(html, 'lxml')
		label = []
		keyword_compile = re.compile(r'<a .*>(.*)<span></span></a>')
		for each_item in soup.find(attrs={"class": "fieed-box"}).find_all('a'):
			if keyword_compile.match(str(each_item)):
				label.append({'label': str(each_item['id']), 'name': keyword_compile.findall(str(each_item))[0]})
		return label

	@classmethod
	def sogou_hotword(cls, html):
		"""
		搜狗热词解析
		:param html:
		:return:
		"""
		logger.debug("开始解析搜狗热词")
		soup = BeautifulSoup(html, 'lxml')
		hotword = []
		for each in soup.find(attrs={"id": "topwords"}).find_all('li'):
			hotword.append({'keyword': each.a.string, 'crawl_url': each.a['href']})
		return hotword

	@classmethod
	def sogou_search_keyword_parse(cls, html):
		"""
		搜狗搜索页解析
		:param html:
		:return: list[{}]
		[
			{
				'cover_url':                # 文章封面图url
				'title':                    # 文章标题
				'content_url':              # 文章地址
				"description":              # 文章描述
				"wechat_avatar":            # 公众号头像
				"wechat_profile_url":       # 公众号临时url
				"wechat_name":              # 公众号名称
			}
		]
		"""
		logger.debug("开始解析搜狗搜索页面")
		soup = BeautifulSoup(html, 'lxml')
		article_list = []

		for _ in soup.find(class_="news-list").find_all('li'):
			try:
				title = "".join(_.find(class_="txt-box").a.strings)
				description = "".join(_.find(class_="txt-box").p.strings)
				if _ is None:
					continue
				if _.find(attrs={"class": "img-box"}) is None:
					continue
				article_list.append({
					'cover_url': "http:" + _.find(attrs={"class": "img-box"}).a.img['src'],
					'title': title,
					'content_url': _.find(class_="txt-box").a['href'],
					"description": description,
					"wechat_avatar": _.find(class_='s-p').a['data-headimage'],
					"wechat_profile_url": _.find(class_='s-p').a['href'],
					"wechat_name": _.find(class_='s-p').a.string
				})
			except:
				continue

		logger.debug("解析搜狗搜索页完成，共解析%s 条文章" % len(article_list))
		return article_list

	@classmethod
	def weibo_tophot_parse(cls, html):
		logger.debug("开始解析微博热词")
		from urllib.parse import urlencode
		soup = BeautifulSoup(html, 'lxml')
		hotword = []
		url = 'https://weixin.sogou.com/weixin??'
		"https://weixin.sogou.com/weixin?type=1&ie=utf8&s_from=hotnews&query=%E6%B1%B6%E5%B7%9D+%E6%B3%A5%E7%9F%B3%E6%B5%81"

		for each in soup.find_all(class_='td-02'):
			parameter = {
				'query':each.a.string,
				'type':2,
				'ie':'utf8',
				's_from':'input',
			}
			hotword.append({'keyword':each.a.string,'crawl_url':url+urlencode(parameter)})
		logger.debug("解析微博热词完成，共 {} 个".format(len(hotword)))
		return hotword

if __name__ == '__main__':
	# file = open('a.html', 'r', encoding='utf-8')
	# str1 = file.read()
	# file.close()
	print(BeautiHtml.weibo_tophot_parse(''))
