#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/25 5:02 PM
@Author  : Larry
@Site    : 
@File    : account.py
@Software: PyCharm
@Desc    :

"""

from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect, reverse
from django.views.generic import View, TemplateView, FormView, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from web_admin.forms import UserLoginForm, UserRegisterForm

import logging
import logging.config
logger = logging.getLogger(__name__)
collect_logger = logging.getLogger("collect")


class UserLoginView(LoginView):
	form_class = UserLoginForm
	template_name = 'users/login.html'
	success_url = '/wechat/index.html'

	def form_valid(self, form):
		auth_login(self.request, form.get_user())
		return HttpResponseRedirect(self.success_url)

	def get_context_data(self, **kwargs):
		return super().get_context_data(**kwargs)

	def post(self, request, *args, **kwargs):

		form = self.get_form()
		if form.is_valid():
			request.session['_uid'] = '222'
			return self.form_valid(form)
		else:
			return self.form_invalid(form)


class UserLogoutView(LogoutView):
	next_page = "/user/login/"

	def get_context_data(self, **kwargs):
		return super().get_context_data(**kwargs)


class UserRegisterView(FormView):
	form_class = UserRegisterForm
	template_name = 'users/register.html'
	success_url = '/user/login/'

	def form_valid(self, form):
		return super().form_valid(form)

	def form_invalid(self, form):
		# print(context)
		return self.render_to_response(self.get_context_data(form=form))

	def post(self, request, *args, **kwargs):

		form = self.get_form()
		if form.is_valid():
			form.save()
			print('form is valid')
			return self.form_valid(form)
		else:
			print(form.errors)
			return self.form_invalid(form)
