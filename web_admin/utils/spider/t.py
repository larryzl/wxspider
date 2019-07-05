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

from web_admin.utils.spider.api import SogouSpider

import requests


def create_random_password(max_pwd=9):
	import random
	from string import ascii_letters,digits
	new_pwd = ''
	for i in range(max_pwd):
		new_pwd += random.choice(ascii_letters) + random.choice(digits)
	return new_pwd
"""
2A37F4DA6E2F940A000000005D1DAB31
2A37F4DA6E2F940A000000005D1DAB31
"""
if __name__ == '__main__':
	ss = SogouSpider()
	keyword = "北京那点事"
	print(ss.get_gzh_info(keyword))
	#
	# r = requests.get('https://weixin.sogou.com')
	# print(r.cookies.get('SUID'))
	#
