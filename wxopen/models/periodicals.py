#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/25 5:09 PM
@Author  : Larry
@Site    : 
@File    : periodicals.py
@Software: PyCharm
@Desc    :

"""

from django.db import models
from uuid import uuid4

# Create your models here.

periodical_type = (
	(100, "电影"),
	(200, "音乐"),
	(300, "句子")
)


class Images(models.Model):
	uuid = models.CharField(unique=True, auto_created=True, default=uuid4, editable=False, primary_key=True,
	                        max_length=50)
	name = models.CharField(max_length=20, verbose_name="图片名称")
	image = models.ImageField(upload_to="img", verbose_name="图片")

	class Meta:
		app_label = 'wxopen'
		db_table = 'images'
		verbose_name = '图片表'
		verbose_name_plural = verbose_name

	def __str__(self):
		return self.name


class Periodicals(models.Model):
	uuid = models.CharField(unique=True, auto_created=True, default=uuid4, editable=False, primary_key=True,
	                        max_length=50)
	title = models.CharField(unique=True, max_length=20, verbose_name="期刊题目")
	content = models.TextField(null=True, blank=True, verbose_name="期刊内容")
	index = models.IntegerField(verbose_name="期号")
	fav_nums = models.IntegerField(verbose_name="点赞次数", default=0, auto_created=True)
	pubdate = models.DateField(auto_now=True, verbose_name="发布日期")
	type = models.IntegerField(verbose_name="类型", choices=periodical_type, blank=False)
	image = models.ForeignKey(Images, on_delete=models.CASCADE)

	class Meta:
		app_label = 'wxopen'
		db_table = 'periodicals'
		verbose_name = '期刊表'
		verbose_name_plural = verbose_name

	def __str__(self):
		return self.title
