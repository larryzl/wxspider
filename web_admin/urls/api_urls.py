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

from web_admin.views import GzhCreate,GzhList,KindCreate,UpdateSogouHotArticleKind,\
	KindList,CrawlGzhHistoryArticle,CrawlSogouHotArticle,ArticleList,UpdateSogouHotword,HotwordList,CrawlKeywordArticle,SogouCookieUpdate

urlpatterns = [
	re_path(r'create/gzh$', GzhCreate.as_view(), name='api_create_gzh'),
	re_path(r'create/kind/?$', KindCreate.as_view(), name='api_create_kind'),

	re_path(r'get/kind/?$', KindList.as_view()),
	re_path(r'get/gzh', GzhList.as_view(), name='api_get_gzh'),
	re_path(r'get/hotword', HotwordList.as_view(), name='api_get_gzh'),
	re_path(r'get/article', ArticleList.as_view(), name='api_get_gzh'),

	re_path(r'pull/hot/article$', CrawlSogouHotArticle.as_view()),
	re_path(r'pull/keyword/article$', CrawlKeywordArticle.as_view()),
	re_path(r'pull/gzh/history$', CrawlGzhHistoryArticle.as_view()),

	re_path(r'update/article/kind$', UpdateSogouHotArticleKind.as_view()),
	re_path(r'update/hotword$', UpdateSogouHotword.as_view()),
	re_path(r'update/cookie',SogouCookieUpdate.as_view()),





]
