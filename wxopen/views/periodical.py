#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/25 10:51 AM
@Author  : Larry
@Site    : 
@File    : periodical.py
@Software: PyCharm
@Desc    :

"""

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from wxopen.models import Periodicals, Images, Appkey
from wxopen.forms import PeriodicalForms, ImageForms, AppkeyForms


# Create your views here.


class PeriodicalView(TemplateView):
	last_periodical = Periodicals.objects.last()
	template_name = "periodical/index.html"
	extra_context = {'PeriodicalForms': PeriodicalForms}

	def get(self, request):
		return render(request, context=self.extra_context, template_name=self.template_name)

	def post(self, request):
		form = PeriodicalForms(request.POST)
		if form.is_valid():
			form.save()
			return redirect('periodical_add')
		else:
			print(form.errors)


class ImageView(TemplateView):
	template_name = "periodical/image.html"
	extra_context = {'ImageForms': ImageForms}

	def get(self, request):
		imgs = Images.objects.all()
		self.extra_context['imgs'] = imgs
		return render(request, context=self.extra_context, template_name=self.template_name)

	def post(self, request):
		img = Images(image=self.request.FILES.get('img'), name=self.request.POST.get("name"))
		img.save()
		return redirect('periodical_add')
