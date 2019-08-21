#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/26 12:02 PM
@Author  : Larry
@Site    : 
@File    : mpwx.py
@Software: PyCharm
@Desc    :

"""

from datetime import date, datetime, timedelta
from uuid import uuid4

from django.db import models

from web_admin.models import CustomUser

AKIND = (
	('zonghe', '综合'),
	('xinwen', '新闻'),
	('gaoxiao', '搞笑'),
	('health', '养生'),
	('sifanghua', '私房话'),
	('gossip', '八卦'),
	('technology', '科技'),
	('finance', '财经'),
	('car', '汽车'),
	('life', '生活'),
	('fashion', '时尚'),
	('mummy', '辣妈 / 育儿'),
	('travel', '旅行'),
	('job', '职场'),
	('food', '美食'),
	('history', '历史'),
	('study', '学霸 / 教育'),
	('constellation', '星座'),
	('sport', '体育'),
	('military', '军事'),
	('game', '游戏'),
	('pet', '萌宠'),
)


# class Kind(models.Model):
# 	uuid = models.CharField(primary_key=True, auto_created=True, default=uuid4, editable=False, max_length=50)
# 	name = models.CharField(verbose_name="分类名称", max_length=30, unique=True)
#
# 	class Meta:
# 		verbose_name = "分类"
# 		verbose_name_plural = verbose_name
#
# 	def __str__(self):
# 		return self.name


class Wechat(models.Model):
	STATUS_DEFAULT = 0
	STATUS_DISABLE = 1
	STATUS_DELETE = 2
	STATUS_CHOICES = (
		(STATUS_DEFAULT, '默认'),
		(STATUS_DISABLE, '禁用'),
		(STATUS_DELETE, '删除')
	)
	avatar = models.CharField(max_length=500, blank=True, default='', verbose_name='公众号头像')
	qrcode = models.CharField(max_length=500, blank=True, default='', verbose_name='二维码')
	name = models.CharField(max_length=100, verbose_name='公众号名称', unique=True)
	wechatid = models.CharField(max_length=100, verbose_name='公众号id', unique=True)
	intro = models.TextField(default='', blank=True, verbose_name='简介')
	crawl_time1 = models.TimeField(null=True, blank=True, verbose_name='爬取时间')
	crawl_time2 = models.TimeField(null=True, blank=True, verbose_name='爬取时间')
	crawl_time3 = models.TimeField(null=True, blank=True, verbose_name='爬取时间')
	create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
	profile_url = models.CharField(max_length=500, blank=True, default='', verbose_name='公众号地址')
	kind = models.ForeignKey('WechatArticleKind', on_delete=models.CASCADE)
	status = models.IntegerField(default=STATUS_DEFAULT, choices=STATUS_CHOICES, verbose_name="状态")
	# user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

	def last_day_topics_count(self):
		yestoday = date.today() - timedelta(days=1)
		yestoday_datetime = datetime.combine(yestoday, datetime.min.time())
		return Article.objects.filter(wechat=self, publish_time__gt=yestoday_datetime).count()

	def last_week_topics_count(self):
		last_week = date.today() - timedelta(days=7)
		last_week_datetime = datetime.combine(last_week, datetime.min.time())
		return Article.objects.filter(wechat=self, publish_time__gt=last_week_datetime).count()

	def total_topics_count(self):
		return Article.objects.filter(wechat=self).count()

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name_plural = "公众号"


class Article(models.Model):
	wechat = models.ForeignKey('Wechat', verbose_name='公众号', related_name='topic', on_delete=models.CASCADE)
	title = models.CharField(max_length=200, verbose_name='文章标题')
	content_url = models.CharField(max_length=500, default='', verbose_name='临时url')
	source_url = models.CharField(max_length=500, default='', verbose_name='原文地址')
	avatar = models.CharField(max_length=500, default='', verbose_name='缩略图地址')
	abstract = models.TextField(default='', verbose_name='内容简介')
	content = models.TextField(default='', verbose_name='文章内容')
	comment_count = models.IntegerField(default=0, verbose_name='评论数')
	read_num = models.IntegerField(default=0, verbose_name='阅读数')
	like_num = models.IntegerField(default=0, verbose_name='点赞数')
	copyright_stat = models.IntegerField(default=0, verbose_name='是否为原创 1 为原创 0 为非原创')
	mas_index = models.IntegerField(default=0, verbose_name='群发中图文顺序,1为头条')
	author = models.CharField(max_length=50, default='', verbose_name='作者')
	publish_time = models.DateTimeField(verbose_name='发布时间')
	create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
	update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
	available = models.CharField(db_index=True, max_length=100, default='', verbose_name='是否可用')
	twpid = models.CharField(max_length=50, default='', verbose_name='文章唯一值',unique=True)
	kind = models.ForeignKey('WechatArticleKind', default='',null=True,blank=True,verbose_name='分类', on_delete=models.CASCADE)
	hotword = models.ForeignKey('Word',default='',null=True,blank=True,verbose_name='热词',on_delete=models.CASCADE)

	def __unicode__(self):
		return self.title

	class Meta:
		verbose_name_plural = "文章"


class WechatArticleKind(models.Model):
	uuid = models.CharField(primary_key=True, auto_created=True, default=uuid4, editable=False, max_length=50)
	name = models.CharField(max_length=200, verbose_name='分类名称')
	label = models.CharField(max_length=200, verbose_name='标题标签')

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = "分类"
		verbose_name_plural = verbose_name

	def __str__(self):
		return self.name


class Proxy(models.Model):
	STATUS_NEW = 0
	STATUS_SUCCESS = 1
	STATUS_FAIL = 2
	STATUS_CHOICES = (
		(STATUS_NEW, '未检测'),
		(STATUS_SUCCESS, '检测成功'),
		(STATUS_FAIL, '检测失败'),
	)
	KIND_SEARCH = 0
	KIND_DOWNLOAD = 1
	KIND_CHOICES = (
		(KIND_SEARCH, '搜索代理'),
		(KIND_DOWNLOAD, '下载代理'),
	)
	kind = models.IntegerField(default=KIND_DOWNLOAD, choices=KIND_CHOICES, verbose_name="类型")
	user = models.CharField(default='', blank=True, max_length=100)
	password = models.CharField(default='', blank=True, max_length=100)
	host = models.CharField(max_length=100)
	port = models.IntegerField(default=80)
	speed = models.IntegerField(default=0, verbose_name="连接速度(ms)")
	status = models.IntegerField(default=STATUS_NEW, choices=STATUS_CHOICES, verbose_name="状态")
	retry = models.IntegerField(default=0, verbose_name="尝试次数")
	create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
	update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

	class Meta:
		verbose_name_plural = "访问代理"


class Word(models.Model):
	keyword = models.CharField(max_length=100, verbose_name='热词')
	frequency = models.IntegerField(default=100, verbose_name='爬取频率, 单位:分钟')
	next_crawl_time = models.DateTimeField(auto_now_add=True, verbose_name='下次爬取时间')
	crawl_url = models.CharField(max_length=500, default='', verbose_name='临时url')
	hwid = models.CharField(max_length=50, default='', verbose_name='热词唯一值')
	create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

	def __unicode__(self):
		return self.text

	class Meta:
		verbose_name_plural = "词"
