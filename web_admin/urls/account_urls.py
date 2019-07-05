#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/25 5:33 PM
@Author  : Larry
@Site    : 
@File    : users_urls.py
@Software: PyCharm
@Desc    :

"""
from django.urls import re_path
from web_admin.views import UserLoginView,UserRegisterView,UserLogoutView

urlpatterns = [
	re_path(r'login/',UserLoginView.as_view(),name='user_login'),
	re_path(r'logout/',UserLogoutView.as_view(),name='user_logout'),
	re_path(r'register/',UserRegisterView.as_view(),name='user_register'),
	# re_path(r'account/(?P<pk>\d+)/profile',)
]