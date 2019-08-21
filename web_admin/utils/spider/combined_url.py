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
	_base_url = 'https://weixin.sogou.com/weixin?'

	@classmethod
	def search_url(cls, keyword, type=1):
		"""拼接搜索公众号URL
		:param type: 1 搜索公众号， 2 搜索文章
		:param keyword: 关键词
		:param page: 搜索页数
		:return:  str
		"""
		for p in range(1, 10):
			if type == 1:
				parameter = {'type': 1, 'page': p, 'ie': 'utf8', 'query': keyword}
			else:
				parameter = {'type': 2, 's_from': 'input', 'query': keyword, 'ie': 'utf8', 'page': p}

			if p == 1:
				parameter.pop('page')
				referer = "/".join(cls._base_url.split('/')[0:-1])
			else:
				r_p = parameter.copy()
				r_p['page'] = p - 1
				referer = cls._base_url + urlencode(r_p)

			yield (cls._base_url + urlencode(parameter), referer)


if __name__ == '__main__':
	url_list = WechatSogouCombinedUrl.search_url(keyword='keyword', type=2)
	for i in url_list:
		print(i)
