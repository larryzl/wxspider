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

from web_admin.models import Wechat, Article, WechatArticleKind, Word
from web_admin.utils import error_code
from web_admin.utils.spider.api import SogouSpider

logger = logging.getLogger(__name__)
logging.getLogger('django')


def update_article_database(article_info, keyword=None):
	for _ in article_info:
		# 判断公众号是否存在
		# wechat_id = _['wechat_id']
		if not Wechat.objects.filter(wechatid=_['wechat_id']).count():
			logger.debug('正在更新公众号信息')
			Wechat.objects.create(
					avatar=_['wechat_avatar'],
					qrcode=_['qrcode'],
					name=_['wechat_name'],
					wechatid=_['wechat_id'],
					intro=_['wechat_desc'],
					profile_url=_['wechat_profile_url'],
					kind=WechatArticleKind.objects.get(label=_['label_name']),
			)
			logger.debug("更新公众号信息完成")
		article_detail = {
			"wechat": Wechat.objects.get(wechatid=_['wechat_id']),
			"title": _['title'],
			"content_url": _['content_url'],
			"source_url": _['source_url'],
			"avatar": _['cover_url'],
			"abstract": _['description'],
			"content": _['content'],
			"copyright_stat": _['copyright_stat'],
			"mas_index": _['msg_index'],
			"author": _['author'],
			"publish_time": _['publish_time'],
			"twpid": _['twpid'],
			"kind": WechatArticleKind.objects.get(label=_['label_name']),
		}
		if keyword is not None:
			article_detail["hotword"] = Word.objects.get(keyword=keyword)
		article_obj = Article(**article_detail)
		article_obj.save()
		logger.debug("创建热门文章完成")


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
				context = {'code': error_code.DATA_ERROR, 'msg': '抓取热门文章失败'}

		logger.debug("开始写入数据，共 %s 条数据需要写入" % len(article_info))

		update_article_database(article_info)


if __name__ == '__main__':
	CrondFunc.CrondCrawlHotArticle()
