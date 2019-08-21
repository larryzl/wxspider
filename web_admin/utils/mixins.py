#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/21 5:27 PM
@Author  : Larry
@Site    : 
@File    : mixins.py
@Software: PyCharm
@Desc    :

"""

from django.contrib.auth.decorators import login_required

class LoginRequireMixin:
	@classmethod
	def as_view(cls, **initkwargs):
		view = super(LoginRequireMixin,cls).as_view(**initkwargs)
		return login_required(view)