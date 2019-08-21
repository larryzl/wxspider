#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/26 12:09 PM
@Author  : Larry
@Site    : 
@File    : manager.py
@Software: PyCharm
@Desc    :

"""
from django import forms
from web_admin.models import Wechat, WechatArticleKind


class WechatForm(forms.ModelForm):
	class Meta:
		model = Wechat
		fields = ['avatar', 'qrcode', 'name', 'wechatid', 'intro']


class KindForm(forms.ModelForm):
	class Meta:
		model = WechatArticleKind
		fields = ['name']