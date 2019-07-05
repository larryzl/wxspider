#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/28 3:25 PM
@Author  : Larry
@Site    : 
@File    : manager_api.py
@Software: PyCharm
@Desc    :

"""

from django.views.generic import View, TemplateView, ListView, CreateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from web_admin.utils.mixins import LoginRequireMixin
from web_admin.models import Wechat
from web_admin.utils.spider.bak import Sgspider
from web_admin.utils import error_code
import json
from web_admin.models import Wechat, CustomUser


class AjaxableResponseMixin:
	def form_invalid(self, form):
		response = super(AjaxableResponseMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):
		# We make sure to call the parent's form_valid() method because
		# it might do some processing (in the case of CreateView, it will
		# call form.save() for example).
		response = super(AjaxableResponseMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'pk': self.object.pk,
			}
			return JsonResponse(data)
		else:
			return response


class JSONResponseMixin:
	"""
	A mixin that can be used to render a JSON response.
	"""

	def render_to_json_response(self, context, **response_kwargs):
		"""
		Returns a JSON response, transforming 'context' to make the payload.
		"""
		return JsonResponse(
				self.get_data(context),
				**response_kwargs
		)

	def get_data(self, context):
		"""
		Returns an object that will be serialized as JSON by json.dumps().
		:param context:
		"""
		# Note: This is *EXTREMELY* naive; in reality, you'll need
		# to do much more complex handling to ensure that arbitrary
		# objects -- such as Django model instances or querysets
		# -- can be serialized as JSON.
		return context


# @method_decorator(csrf_exempt,)
class GzhCreate(LoginRequireMixin, JSONResponseMixin, CreateView):
	model = Wechat
	fields = ['name', 'wechatid', 'frequency']

	def post(self, request, *args, **kwargs):
		"""

		:param request:
		:param args:
		:param kwargs:
		:return:
		"""
		status = error_code.STATUS_ERROR
		try:
			ajax_data = request.POST.get('data')
			if not ajax_data:
				response_data = "ajax data type error"
			else:
				wechatid = json.loads(ajax_data).get('wechatid', '')
				frequency = int(json.loads(ajax_data).get('frequency', ''))

				### 调用接口搜索公众号信息
				if wechatid is not None and frequency is not None:
					# Sgspider.test_get_article_content()
					wgz_info = Sgspider.get_gzh_info(wechatid)
					# print("wgz_info:", wgz_info)
					if wgz_info is not None:
						image_name = Sgspider.save_image(wgz_info['headimage'])
						if image_name[0] == 0:
							image_name[1] = "/static/images/wx/" + image_name[1]
						else:
							image_name[1] = wgz_info['headimage']
						# print("image_name: ", image_name[1])
						status = error_code.STATUS_OK
						response_data = '添加成功'
						user = CustomUser.object.get(username=request.user.username)
						wc = Wechat.objects.create(avatar=image_name[1], qrcode=wgz_info['qrcode'],
						                           name=wgz_info['wechat_name'], wechatid=wgz_info['wechat_id'],
						                           intro=wgz_info['introduction'], frequency=frequency, user=user)
						wc.save()
					else:
						response_data = "公众号没有找到"
				else:
					response_data = "wechatid or 抓取频率 错误"

			# print(response_data)
			context = {'status': status, 'data': response_data}
			# print(context)
		# print(type(wechatid))
		except Exception as e:
			# print(e)
			context = {'status': status, 'data': e}

		return JsonResponse(self.get_data(context=context))
