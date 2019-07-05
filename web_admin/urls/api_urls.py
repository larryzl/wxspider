#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/28 3:23 PM
@Author  : Larry
@Site    : 
@File    : api_urls.py
@Software: PyCharm
@Desc    :

"""

from django.urls import re_path
from web_admin.views import GzhCreate

urlpatterns = [
	re_path(r'create/gzh$', GzhCreate.as_view(), name='api_create_gzh'),
]