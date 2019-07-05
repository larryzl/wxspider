#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/26 5:21 PM
@Author  : Larry
@Site    : 
@File    : account.py
@Software: PyCharm
@Desc    :

"""

from django.db import models
from uuid import uuid4
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class CustomUserManager(BaseUserManager):
	def _create_user(self, username, email, password, **extra_fields):
		"""
		Create and saves a User with the given username,email, date of birth and password
		:param email:
		:param date_of_birth:
		:param password:
		:return:
		"""

		assert email
		assert username

		now = timezone.now()

		user = self.model(
				username=username,
				email=self.normalize_email(email),
				last_login=now,
				date_joined=now,
				**extra_fields
		)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, username, email, password, **extra_fields):
		return self._create_user(username, email, password, **extra_fields)

	def create_superuser(self,username,email,password,**extra_fields):
		return self._create_user(username,email,password,is_admin=True)


class CustomUser(AbstractBaseUser):
	uuid = models.CharField(primary_key=True, auto_created=True, default=uuid4, editable=False, max_length=50)
	email = models.EmailField(verbose_name="邮箱地址", max_length=254, unique=True)
	username = models.CharField(verbose_name="用户名", max_length=30, unique=True)
	nickname = models.CharField(max_length=64, blank=True, verbose_name='昵称')
	first_name = models.CharField(verbose_name="名字", max_length=30, blank=False)
	last_name = models.CharField(verbose_name="姓氏", max_length=30, blank=False)
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)
	mobile = models.CharField(verbose_name="手机号码", max_length=30, blank=False)
	date_joined = models.DateTimeField(verbose_name="创建时间", default=timezone.now)

	object = CustomUserManager()

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = []

	def get_full_name(self):
		return '%s %s' % (self.first_name, self.last_name)

	def get_short_name(self):
		return self.first_name

	def __str__(self):
		return self.email

	@property
	def is_staff(self):
		return self.is_admin

	class Meta:
		verbose_name = "用户管理"
		verbose_name_plural = verbose_name
