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
import sys
import logging.config
import hashlib

from web_admin.models import WechatArticleKind, Word
from web_admin.utils.spider.api import SogouSpider
from web_admin.views import update_article_database

logger = logging.getLogger(__name__)
logging.getLogger('django')


class CrondFunc:
	@classmethod
	def crond_crawl_hot_article(cls):
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

	@classmethod
	def crond_crawl_keyword_article(cls, kind=0, crawl_num=10):
		# 更新keyword
		sg = SogouSpider()
		logger.debug('更新分类：{}'.format(kind))
		if int(kind) == 0:
			hotword_list = sg.update_sogou_hotword()
			if len(hotword_list) > 0:
				for item in hotword_list:
					hwid = hashlib.md5(str(item['keyword']).encode()).hexdigest()
					if not Word.objects.filter(hwid=hwid).count():
						Word.objects.update_or_create(keyword=item['keyword'],
						                              crawl_url=item['crawl_url'], hwid=hwid, kind=0)

		else:
			hotword_list = sg.update_weibo_hotword()
			if len(hotword_list) > 0:
				for item in hotword_list:
					hwid = hashlib.md5(str(item['keyword']).encode()).hexdigest()
					if not Word.objects.filter(hwid=hwid).count():
						Word.objects.create(keyword=item['keyword'],
						                    crawl_url=item['crawl_url'], hwid=hwid, kind=1)

		for keyword in hotword_list:

			logger.debug('抓取关键词:{}'.format(keyword))
			article_info = sg.crawl_keyword_articles(keyword=keyword, crawl_max=crawl_num)

			if not Word.objects.filter(keyword=keyword).count():
				Word.objects.update_or_create(keyword=keyword)

			update_article_database(article_info, keyword=keyword)


if __name__ == '__main__':
	if sys.argv[1] == 'hotarticle':
		CrondFunc.crond_crawl_hot_article()
	elif sys.argv[1] == 'keyword':
		CrondFunc.crond_crawl_keyword_article(kind=sys.argv[2], crawl_num=sys.argv[3])
