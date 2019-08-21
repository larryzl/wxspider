#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/26 11:29 AM
@Author  : Larry
@Site    : 
@File    : manager_url.py
@Software: PyCharm
@Desc    :

"""
from django.urls import re_path
from web_admin.views import IndexView, TestView, ArticleView, HotwordView

urlpatterns = [
	re_path(r'index.html$',IndexView.as_view(),name='manager_index'),
	re_path(r'article.html$',ArticleView.as_view()),
	re_path(r'hotword.html$',HotwordView.as_view()),
	re_path(r'add_gzh.html$',TestView.as_view()),

]