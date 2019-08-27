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

		kind = int(kind)

		if kind == 0:
			hotword_list = sg.update_sogou_hotword()
		else:
			hotword_list = sg.update_weibo_hotword()
		if not isinstance(hotword_list, list):
			logger.error("获取关键词格式错误")
			assert "获取关键词格式错误"

		if len(hotword_list) <= 0:
			logger.error("获取关键词数量为0")
			return False

		keyword_num = 0
		for _ in hotword_list:

			keyword = _.get('keyword', None)
			if keyword is not None:
				logger.error('未获取到关键词，跳过')
				continue
			else:
				logger.debug('抓取关键词: {}'.format(keyword))
				keyword_num += 1

			hwid = hashlib.md5(str(keyword).encode()).hexdigest()

			if not Word.objects.filter(hwid=hwid).count():
				# 如果不存在 hwid 创建关键词
				try:
					Word.objects.create(keyword=keyword,
					                    crawl_url=_['crawl_url'], hwid=hwid, kind=kind)
					logger.debug('创建关键词成功, 关键词: {} . 关键词hwid: {}'.format(keyword, hwid))
				except Exception as e:
					logger.error('创建关键词错误，关键词: {} ,错误原因: {}'.format(keyword, e))
			else:
				logger.debug('关键词: {} 已存在'.format(keyword))

			article_info = sg.crawl_keyword_articles(keyword=keyword, crawl_max=crawl_num)

			if not isinstance(article_info, list):
				logger.error('抓取文章信息失败,文章关键词: {}'.format(keyword))
				continue

			update_article_database(article_info, keyword=keyword)


if __name__ == '__main__':
	if sys.argv[1] == 'hotarticle':
		CrondFunc.crond_crawl_hot_article()
	elif sys.argv[1] == 'keyword':
		CrondFunc.crond_crawl_keyword_article(kind=sys.argv[2], crawl_num=sys.argv[3])
