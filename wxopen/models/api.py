#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/25 5:25 PM
@Author  : Larry
@Site    : 
@File    : api.py
@Software: PyCharm
@Desc    :

"""
from django.db import models
from uuid import uuid4


class Appkey(models.Model):
	uuid = models.CharField(unique=True, auto_created=True, default=uuid4, editable=False, primary_key=True,
	                        max_length=50)
	key = models.CharField(unique=True, max_length=20, verbose_name="appkey")

	class Meta:
		app_label = 'wxopen'
		db_table = 'appkey'
		verbose_name = ''
		verbose_name_plural = verbose_name

	def __str__(self):
		return self.key
