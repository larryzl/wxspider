#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/2 2:28 PM
@Author  : Larry
@Site    :
@File    : api.py
@Software: PyCharm
@Desc    :

"""

import requests

import json


class A:
	def __init__(self):
		self.__value = 'www.a.com'

	@property
	def value(self):
		return self.__value

	@value.setter
	def value(self, value):
		self.__value = value

	def mt(self):
		a = {
			'a': 'a',
			'b': self.__value,
		}
		print(a)


def main():
	# 配置您申请的APPKey
	appkey = "2492b5f4a3ab1e54978fe859c0dd79cc"

	# 1.识别验证码
	# request1(appkey, "POST")
	t = A()
	t.mt()


# 2.查询验证码类型代码
from requests_toolbelt import MultipartEncoder


# 识别验证码
def request1(appkey, m="GET"):
	file = "code.png"
	url = "http://op.juhe.cn/vercode/index"

	import base64
	with open(file, 'rb') as f:
		data = f.read()
		encodestr = base64.b64encode(data)
	params = {
		"key": appkey,
		"codeType": "1006",
		"base64Str": encodestr,
		"dtype": "json",  # 返回的数据的格式，json或xml，默认为json

	}
	response = requests.post(url, data=params)
	res = response.json()
	print(res)

	if res:
		error_code = res["error_code"]
		if error_code == 0:
			# 成功请求
			print(res["result"])
		else:
			print("%s:%s" % (res["error_code"], res["reason"]))
	else:
		print("request api error")


if __name__ == "__main__":
	main()
