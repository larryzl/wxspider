#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/22 11:31 AM
@Author  : Larry
@Site    : 
@File    : crontab.py
@Software: PyCharm
@Desc    : 定时任务

"""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

import logging
import logging.config

from web_admin.models import WechatArticleKind
from web_admin.utils.spider.api import SogouSpider
from web_admin.views import update_article_database

logger = logging.getLogger(__name__)
logging.getLogger('django')


class CrondFunc:
	@classmethod
	def CrondCrawlHotArticle(cls):
		kind_list = [k.label for k in WechatArticleKind.objects.all()]
		sg = SogouSpider()

		article_info = []
		for k in kind_list:
			try:
				article_info.extend(sg.crawl_hotpage_articles(crawl_max=50, label_name=k))
			except Exception as e:
				logger.error('抓取热门文章失败')
				logger.error(e)

		logger.debug("开始写入数据，共 %s 条数据需要写入" % len(article_info))

		update_article_database(article_info)


if __name__ == '__main__':
	CrondFunc.CrondCrawlHotArticle()
