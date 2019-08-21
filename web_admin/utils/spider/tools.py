#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/3 11:06 AM
@Author  : Larry
@Site    : 
@File    : tools.py
@Software: PyCharm
@Desc    :

"""

import requests
import ast
import urllib.parse as url_parse


def _replace_str_html(s):
	"""替换html‘&quot;’等转义内容为正常内容

	Args:
		s: 文字内容

	Returns:
		s: 处理反转义后的文字
	"""
	html_str_list = [
		('&#39;', '\''),
		('&quot;', '"'),
		('&amp;', '&'),
		('&yen;', '¥'),
		('amp;', ''),
		('&lt;', '<'),
		('&gt;', '>'),
		('&nbsp;', ' '),
		('\\', '')
	]
	for i in html_str_list:
		s = s.replace(i[0], i[1])
	return s


def replace_html(data):
	if isinstance(data, dict):
		return dict([(replace_html(k), replace_html(v)) for k, v in data.items()])
	elif isinstance(data, list):
		return [replace_html(l) for l in data]
	elif isinstance(data, str) or isinstance(data, ascii):
		return _replace_str_html(data)
	else:
		return data


def str_to_dict(json_str):
	json_dict = ast.literal_eval(json_str)
	return replace_html(json_dict)


def replace_space(s):
	return s.replace(' ', '').replace('\r\n', '')


def get_url_param(url):
	result = url_parse.urlparse(url)
	return url_parse.parse_qs(result.query, True)


def format_image_url(url):
	if isinstance(url, list):
		return [format_image_url(i) for i in url]

	if url.startswith('//'):
		url = 'https:{}'.format(url)
	return url


def may_int(i):
	try:
		return int(i)
	except Exception:
		return i


DEBUG = True


def d_print(data):
	if DEBUG: print(data)
