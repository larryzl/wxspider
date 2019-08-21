#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/3 11:33 AM
@Author  : Larry
@Site    : 
@File    : t.py
@Software: PyCharm
@Desc    :

"""


class sogouSpider:
	def __init__(self):
		self.lis = []

	def s1(self):
		lis2 = []
		self.s2(lis2)
		print(self.lis)
		self.s2(self.lis)
		print(self.lis)
		print(lis2)

	def s2(self, lis):
		assert isinstance(lis, list)
		lis.extend([x for x in range(10)])


if __name__ == '__main__':
	m = sogouSpider()
	m.s1()
