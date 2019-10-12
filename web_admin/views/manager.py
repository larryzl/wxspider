#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/26 11:25 AM
@Author  : Larry
@Site    : 
@File    : vendor.py
@Software: PyCharm
@Desc    :

"""

import datetime

from django.views.generic import TemplateView

from web_admin.models import Wechat, Article, WechatArticleKind
from web_admin.utils.mixins import LoginRequireMixin


def get_weekday():
    """
    返回本周一日期
    :return:
    """
    d = datetime.date.today()
    for i in range(6):
        timedelta = datetime.timedelta(days=i)
        dt = d - timedelta
        if dt.weekday() == 0:
            return dt



class TestView(LoginRequireMixin, TemplateView):
    template_name = 'manager/add_gzh.html'


class IndexView(LoginRequireMixin, TemplateView):
    template_name = 'manager/index.html'

    def get(self, request, *args, **kwargs):
        title = "公众号"
        wechat = Wechat.objects.all()
        wechat_num = Wechat.objects.all().count()
        article_kind = WechatArticleKind.objects.all().order_by('label')
        article_all = Article.objects.all().count()
        article_today = Article.objects.filter(create_time__gte=datetime.datetime.now().date()).count()
        article_week = Article.objects.filter(create_time__gte=get_weekday()).count()
        nickname = request.user.nickname
        context = self.get_context_data(nickname=nickname, wechat=wechat, kind=article_kind, wechat_num=wechat_num,
                                        article_all=article_all, title=title,
                                        article_today=article_today, article_week=article_week
                                        , **kwargs)
        # context = self.get_context_data(wechat_num=wechat_num)
        return self.render_to_response(context)


class ArticleView(LoginRequireMixin, TemplateView):
    template_name = 'manager/article.html'

    def get(self, request, *args, **kwargs):
        title = "文章列表"
        wechat_num = Wechat.objects.all().count()
        article = Article.objects.all().order_by('-publish_time').filter(kind__label='pc_0')
        article_all = Article.objects.all().count()
        article_today = Article.objects.filter(create_time__gte=datetime.datetime.now().date()).count()
        article_week = Article.objects.filter(create_time__gte=get_weekday()).count()
        article_kind = WechatArticleKind.objects.all().order_by('label')

        context = self.get_context_data(article=article, article_all=article_all, wechat_num=wechat_num,
                                        article_kind=article_kind,
                                        title=title, article_today=article_today, article_week=article_week)
        return self.render_to_response(context)


class HotwordView(LoginRequireMixin, TemplateView):
    template_name = 'manager/hotword.html'

    def get(self, request, *args, **kwargs):
        title = "文章列表"
        wechat_num = Wechat.objects.all().count()

        article_all = Article.objects.all().count()
        article_today = Article.objects.filter(create_time__gte=datetime.datetime.now().date()).count()
        article_week = Article.objects.filter(create_time__gte=get_weekday()).count()

        context = self.get_context_data(article_all=article_all, wechat_num=wechat_num,
                                        title=title, article_today=article_today, article_week=article_week)
        return self.render_to_response(context)
