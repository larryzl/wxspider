#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/30 5:08 PM
@Author  : Larry
@Site    : 
@File    : cache.py
@Software: PyCharm
@Desc    :

"""

from werkzeug.contrib.cache import FileSystemCache



class WechatCache:

	def __init__(self,cache_dir='cache', default_timeout=300):

		self.cache = FileSystemCache(cache_dir=cache_dir, default_timeout=default_timeout)

	def clear(self):
		return self.cache.clear()

	def get(self,key):
		return self.cache.get(key)

	def add(self,key,value,timeout=None):
		return self.cache.add(key,value,timeout)

	def set(self,key, value, timeout=None):
		return self.cache.set(key,value,timeout)

	def delete(self,key):
		return self.cache.delete(key)

if __name__ == '__main__':
	cache = WechatCache()
	import requests

	r = requests.session()
	print(cache.set('1',r))
	print(cache.get('1'),type(cache.get('1')))
