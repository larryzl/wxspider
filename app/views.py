#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/22 12:04 PM
@Author  : Larry
@Site    : 
@File    : views.py
@Software: PyCharm
@Desc    :

"""

from django.shortcuts import render_to_response, render
from django.views.generic import TemplateView

from web_admin.utils.mixins import LoginRequireMixin



def page_not_found(requests, **kwargs):
	template_name = 'error_pages/404.html'
	response = render(requests,template_name)
	response.status_code = 404
	return response
