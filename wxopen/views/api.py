#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/25 10:53 AM
@Author  : Larry
@Site    : 
@File    : periodical_api.py
@Software: PyCharm
@Desc    :

"""

import json

from django.views.generic import View

from wxopen.models import Periodicals, Appkey
from django.shortcuts import HttpResponse
from django.core import serializers
from django.http import JsonResponse



class LatestPeriodicalApi(View):
	"""
	获取最近的一个期刊内容
	"""
	def get(self,request):
		last_periodical = Periodicals.objects.last()

		response_data = {}
		appkey = self.request.META.get('HTTP_APPKEY')
		if self.request.is_ajax:

			appkey_islegal = Appkey.objects.filter(key=appkey)
			print(appkey_islegal)
			response_data['result'] = serializers.serialize('json',last_periodical)

		else:
			appkey_islegal = Appkey.objects.filter(key=appkey)
			print(appkey_islegal)

		return HttpResponse(JsonResponse(response_data),content_type="application/json")

	def post(self,request):
		if self.request.is_ajax:
			pass
		else:
			pass