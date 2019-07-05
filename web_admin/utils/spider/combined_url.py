#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/5 1:38 PM
@Author  : Larry
@Site    : 
@File    : combined_url.py
@Software: PyCharm
@Desc    :

"""

from urllib.parse import urlencode


class WechatSogouCombinedUrl:
	_search_type = (1,2)
	_base_url = 'https://weixin.sogou.com/weixin?'

	@classmethod
	def gzh_search_url(cls,keyword,page=1):
		"""拼接搜索公众号URL
		:param keyword:
		:param page:
		:return:  str
		"""
		assert isinstance(page,int) and page > 0

		parameter = {
			'type': cls._search_type[0],
			'page': page,
			'ie': 'utf8',
			'query': keyword
		}
		return cls._base_url+urlencode(parameter)

	@classmethod
	def article_url(cls,keyword,page=1):
		pass
