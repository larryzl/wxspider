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

from bs4 import BeautifulSoup


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


if __name__ == '__main__':
	file = open('a.html', 'r', encoding='utf-8')
	str1 = file.read()
	print(BeautiHtml.gzh_parse(str1))
