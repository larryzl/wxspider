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

import datetime
import hashlib
import json
import logging
import logging.config
import os

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.views.generic import View, CreateView

from web_admin.models import Wechat, CustomUser, Article, WechatArticleKind, Word
from web_admin.utils import error_code
from web_admin.utils.mixins import LoginRequireMixin
from web_admin.utils.spider.api import SogouSpider
from app.settings import WXSTATIC_ROOT, WXSTATIC_DIR

logger = logging.getLogger(__name__)
logging.getLogger('django')


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
		ajax_data = request.POST.get('data')
		context = {'code': error_code.STATUS_ERROR, 'msg': ''}
		if not ajax_data:
			context['msg'] = "数据格式传输错误"
			return JsonResponse(self.get_data(context=context))

		wechatid = json.loads(ajax_data).get('gzhName', None)
		crawl_time1 = json.loads(ajax_data).get('time1', None)
		crawl_time2 = json.loads(ajax_data).get('time2', None)
		crawl_time3 = json.loads(ajax_data).get('time3', None)
		kind = json.loads(ajax_data).get('kind', None)
		if wechatid is None or kind is None:
			context['msg'] = "公众号 或 分类错误"
			return JsonResponse(self.get_data(context=context))
		wechatid = wechatid.replace('\n', '').replace(' ', '')
		if len(Wechat.objects.filter(Q(name=wechatid) | Q(wechatid=wechatid))) > 0:
			context['msg'] = "公众号%s已存在" % wechatid
			return JsonResponse(self.get_data(context=context))

		# 调用抓取接口
		ss = SogouSpider()
		gzh_info = ss.get_gzh_info(wechatid)
		if gzh_info is None:
			context['msg'] = "有找到公众号: %s" % wechatid
			return JsonResponse(self.get_data(context=context))

		# 保存数据
		try:
			user = CustomUser.object.get(username=request.user.username)
			avatar = "/static/images/wechat/avatar/" + gzh_info['headimage'].split('/')[-1] + ".png"
			qrcode = avatar.replace('.png', '_qrcode.png')
			wc = Wechat(avatar=avatar, qrcode=qrcode,
			            name=gzh_info['wechat_name'], wechatid=gzh_info['wechat_id'],
			            intro=gzh_info['introduction'], crawl_time1=crawl_time1,
			            user=user,
			            profile_url=gzh_info['profile_url'],
			            kind=WechatArticleKind.objects.get(uuid=kind))
			if crawl_time2:
				wc.crawl_time2 = crawl_time2
			if crawl_time3:
				wc.crawl_time3 = crawl_time3
			wc.save()
			context['msg'] = "公众号%s添加成功" % wechatid
			context['code'] = error_code.STATUS_OK
			return JsonResponse(self.get_data(context=context))
		except IntegrityError:
			context['msg'] = "公众号%s已存在" % wechatid
		except Exception as e:
			context['msg'] = "公众号%s添加错误: %s" % (wechatid, e)
		return JsonResponse(self.get_data(context=context))


class KindCreate(LoginRequireMixin, JSONResponseMixin, CreateView):
	model = WechatArticleKind
	fields = ['name']

	def get(self, requests):
		return JsonResponse(self.get_data({'code': 405, 'msg': 'Method GET not Allow'}))

	def post(self, request, *args, **kwargs):
		resp_code, resp_msg = error_code.STATUS_ERROR, "添加失败"
		ajax_data = request.POST.get('data')
		if len(ajax_data) == 0:
			resp_code += "名称不能为空!"
		else:
			# is_exist = self.model.objects.filter(name=ajax_data)
			# if is_exist:
			# 	resp_msg = "添加失败, %s 已存在"% ajax_data
			try:
				kc = self.model.objects.create(name=ajax_data)
				kc.save()
				resp_msg = "添加成功!"
			except IntegrityError as e:
				resp_msg += "%s已经存在" % ajax_data
			except Exception as e:
				resp_msg += str(e)
		context = {'code': resp_code, 'msg': resp_msg}
		return JsonResponse(self.get_data(context=context))


class ArticleList(LoginRequireMixin, JSONResponseMixin, View):
	"""
	获取文章列表接口
	post：返回json数据
	"""

	def get(self, request):
		return JsonResponse(self.get_data({'code': 405, 'msg': 'Method GET not Allow'}))

	def post(self, request):
		post_data = request.POST
		context = {
			'code': 500,
			'msg': 'Server Error'
		}
		try:
			kind = post_data.get('kind', 'pc_0')
		except:
			return JsonResponse(self.get_data(context))

		article_list = Article.objects.filter(kind__label=kind).order_by('-publish_time')[:20]
		resp_article = []

		for each_article in article_list:
			try:
				gzh = each_article.wechat.name
				gzh_id = each_article.wechat.wechatid
			except:
				gzh = 'null'
				gzh_id = 0
			resp_article.append({
				'title': each_article.title,
				'publish_time': each_article.publish_time,
				'gzh': gzh,
				'abstract': each_article.abstract,
				'avatar': each_article.avatar,
				'gzh_id': gzh_id
			})

		context['code'] = 200
		context['msg'] = resp_article
		return JsonResponse(self.get_data(context))


class GzhList(LoginRequireMixin, JSONResponseMixin, View):
	def get(self, request):
		return JsonResponse(self.get_data({'code': 405, 'msg': 'Method GET not Allow'}))

	def post(self, request):
		post_data = request.POST
		search_kind_name = post_data.get('columns[5][search][value]')
		# print(search_kind_name)

		gzh_list = Wechat.objects.all()
		if search_kind_name:
			gzh_list = gzh_list.filter(kind__uuid=search_kind_name)

		result_length = gzh_list.count()
		display_length = request.POST.get('length', 10)
		display_start = int(request.POST.get('start', 0))
		draw = post_data.get('draw', 1)
		# 分页设置
		paginator = Paginator(gzh_list, display_length)
		try:
			gzh_list = paginator.page(display_start / 10 + 1)
		except PageNotAnInteger:
			gzh_list = paginator.page(1)
		except EmptyPage:
			gzh_list = paginator.page(paginator.num_pages)

		# ajax返回数据

		ajax_response_data = []
		for gzh in gzh_list:
			# 计算离当前时间最近的时间
			time_list = [t for t in [gzh.crawl_time1, gzh.crawl_time2, gzh.crawl_time3] if t is not None]
			now = datetime.datetime.now().time()
			today_time = [t for t in time_list if t >= now]
			tomorrow_time = [[t for t in time_list if t < now]]
			next_crawl_time = min(tomorrow_time) if len(today_time) == 0 else min(today_time)
			try:
				total = gzh.total_topics_count()
			except Exception as e:
				total = 0
			row = {
				'id': gzh.id,
				'avatar': gzh.avatar,
				'name': gzh.name,
				'qrcode': gzh.qrcode,
				'wechatid': gzh.wechatid,
				'status': gzh.status,
				'kind': gzh.kind.name,
				'next_crawl_time': next_crawl_time,
				'last_day': gzh.last_day_topics_count(),
				'last_week': gzh.last_week_topics_count(),
				'total': total,
				'profile_url': gzh.profile_url,
				'intro': gzh.intro
			}

			ajax_response_data.append(row)

		data_table = {
			'data': ajax_response_data,
			'draw': draw,
			'recordsTotal': result_length,
			'recordsFiltered': result_length
		}
		return JsonResponse(self.get_data(context=data_table))


class SogouCookieUpdate(LoginRequireMixin, JSONResponseMixin, View):
	def get(self, request):
		return JsonResponse(self.get_data({'code': 405, 'msg': 'Method GET not Allow'}))

	def post(self, request):
		sg = SogouSpider()
		sg.update_cookie()
		return JsonResponse(self.get_data(context={'code': 200, 'msg': '更新成功'}))


class HotwordList(LoginRequireMixin, JSONResponseMixin, View):
	def get(self, request):
		return JsonResponse(self.get_data({'code': 405, 'msg': 'Method GET not Allow'}))

	def post(self, request):
		post_data = request.POST
		# print(search_kind_name)

		hotword_list = Word.objects.all().order_by('-create_time')

		result_length = hotword_list.count()
		display_length = request.POST.get('length', 10)
		display_start = int(request.POST.get('start', 0))
		draw = post_data.get('draw', 1)
		# 分页设置
		paginator = Paginator(hotword_list, display_length)
		try:
			hotword_list = paginator.page(display_start / 10 + 1)
		except PageNotAnInteger:
			hotword_list = paginator.page(1)
		except EmptyPage:
			hotword_list = paginator.page(paginator.num_pages)

		# ajax返回数据

		ajax_response_data = []
		for hotword in hotword_list:
			# 计算离当前时间最近的时间
			try:
				topic_all = hotword.article_set.all().count()
			except Exception as e:
				logger.error(e)
				topic_all = 0
			row = {
				'id': hotword.id,
				'keyword': hotword.keyword,
				'crawl_url': hotword.crawl_url,
				'article': topic_all,
				'create_time': hotword.create_time,
				'intro': hotword.id,
			}

			ajax_response_data.append(row)

		data_table = {
			'data': ajax_response_data,
			'draw': draw,
			'recordsTotal': result_length,
			'recordsFiltered': result_length
		}
		return JsonResponse(self.get_data(context=data_table))


class KindList(LoginRequireMixin, JSONResponseMixin, View):
	def get(self, request):
		kind_all = WechatArticleKind.objects.all()
		resp_data = []
		for k in kind_all:
			resp_data.append({
				'uuid': k.uuid,
				'name': k.name
			})
		return JsonResponse(self.get_data(context={'data': resp_data}))


def update_article_database(article_info, keyword=None):
	for _ in article_info:
		# 判断公众号是否存在
		# wechat_id = _['wechat_id']
		if not Wechat.objects.filter(wechatid=_['wechat_id']).count():
			logger.debug('正在更新公众号信息')
			Wechat.objects.create(
					avatar=_['wechat_avatar'],
					qrcode=_['qrcode'],
					name=_['wechat_name'],
					wechatid=_['wechat_id'],
					intro=_['wechat_desc'],
					profile_url=_['wechat_profile_url'],
					kind=WechatArticleKind.objects.get(label=_['label_name']),
			)
			logger.debug("更新公众号信息完成")
		article_detail = {
			"wechat": Wechat.objects.get(wechatid=_['wechat_id']),
			"title": _['title'],
			"content_url": _['content_url'],
			"source_url": _['source_url'],
			"avatar": _['cover_url'],
			"abstract": _['description'],
			"content": _['content'],
			"copyright_stat": _['copyright_stat'],
			"mas_index": _['msg_index'],
			"author": _['author'],
			"publish_time": _['publish_time'],
			"twpid": _['twpid'],
			"kind": WechatArticleKind.objects.get(label=_['label_name']),
		}
		if keyword is not None:
			article_detail["hotword"] = Word.objects.get(keyword=keyword)
		article_obj = Article(**article_detail)
		article_obj.save()
		logger.debug("创建热门文章完成")


class CrawlSogouHotArticle(LoginRequireMixin, JSONResponseMixin, View):
	"""
	搜狗热门文章抓取
	"""

	def get(self, requests):
		return JsonResponse(self.get_data({'code': error_code.METHOD_ERROR, 'msg': 'Method GET not Allow'}))

	def post(self, requests):
		"""
		热门文章抓取接口
		:param requests:
		:return:
		"""
		post_data = requests.POST
		logger.error(post_data)
		try:
			kind = post_data.get('kind', 'pc_0')
			pull_article_num = int(post_data.get('pull_num', 1))
		except Exception as e:
			context = {'code': error_code.DATA_ERROR, 'msg': str(e)}
			return JsonResponse(self.get_data(context))

		kind_list = [k.label for k in WechatArticleKind.objects.all()] if kind == 'all' else [kind]

		#
		sg = SogouSpider()

		article_info = []
		for k in kind_list:
			try:
				article_info.extend(sg.crawl_hotpage_articles(crawl_max=pull_article_num, label_name=k))
			except Exception as e:
				logger.error('抓取热门文章失败')
				logger.error(e)
				context = {'code': error_code.DATA_ERROR, 'msg': '抓取热门文章失败'}
				return JsonResponse(self.get_data(context))

		logger.debug("开始写入数据，共 %s 条数据需要写入" % len(article_info))

		update_article_database(article_info)

		context = {
			'msg': len(article_info),
			'code': error_code.STATUS_OK
		}
		return JsonResponse(self.get_data(context))


class UpdateSogouHotArticleKind(LoginRequireMixin, JSONResponseMixin, View):
	def get(self, requests):
		return JsonResponse(self.get_data({'code': 405, 'msg': 'Method GET not Allow'}))

	def post(self, requests):
		context = {
			'code': error_code.STATUS_OK,
			'msg': '更新完成'
		}
		sg = SogouSpider()
		kind = sg.update_wechat_article_kind()
		if len(kind) > 0:
			for item in kind:
				WechatArticleKind.objects.update_or_create(defaults={'name': item['name']}, name=item['name'],
				                                           label=item['label'])
		else:
			context = {
				'code': error_code.STATUS_ERROR,
				'msg': '更新失败'
			}
		return JsonResponse(self.get_data(context))


class UpdateSogouHotword(LoginRequireMixin, JSONResponseMixin, View):
	"""更新搜狗热词
	"""

	def get(self, requests):
		return JsonResponse(self.get_data({'code': 405, 'msg': 'Method GET not Allow'}))

	def post(self, requests):
		context = {'code': error_code.STATUS_ERROR, 'msg': ''}
		sg = SogouSpider()
		hotword_list = sg.update_sogou_hotword()
		if len(hotword_list) > 0:
			for item in hotword_list:
				hwid = hashlib.md5(str(item['keyword']).encode()).hexdigest()
				Word.objects.update_or_create(defaults={'hwid': hwid}, keyword=item['keyword'],
				                              crawl_url=item['crawl_url'], hwid=hwid)
			context.update({'code': error_code.STATUS_OK, 'msg': len(hotword_list)})
		else:
			context.update({'code': error_code.STATUS_ERROR, 'msg': '更新热词失败'})
		return JsonResponse(self.get_data(context))


class CrawlGzhHistoryArticle(LoginRequireMixin, JSONResponseMixin, View):
	""" 抓取公众号历史文章接口
	"""

	def get(self, requests):
		return JsonResponse(self.get_data({'code': 405, 'msg': 'Method GET not Allow'}))

	def post(self, requests):
		context = {
			'code': error_code.STATUS_ERROR,
			'msg': ''
		}
		post_data = requests.POST

		try:
			uuid = post_data.get('uid')
			pull_article_num = post_data.get('pull_num', 5)
		except Exception as e:
			context['code'] = error_code.DATA_ERROR
			context['msg'] = str(e)
			return JsonResponse(self.get_data(context))

		try:
			gzh_obj = Wechat.objects.get(pk=uuid)
		except Exception as e:
			context['msg'] = 'cannot relove keyword'
			return JsonResponse(self.get_data(context))

		try:
			sg = SogouSpider()
			sg.crawl_hotpage_articles()
		except Exception as e:
			pass

		return JsonResponse(self.get_data(context))


class CrawlKeywordArticle(LoginRequireMixin, JSONResponseMixin, View):
	"""
	搜狗热词文章爬取
	"""

	def get(self, requests):
		return JsonResponse(self.get_data({'code': error_code.METHOD_ERROR, 'msg': 'Method GET not Allow'}))

	def post(self, requests):
		post_data = requests.POST
		logger.error(post_data)

		keyword = post_data.get('keyword')
		crawl_url = post_data.get('crawl_url', None)
		crawl_num = post_data.get('crawl_num', 5)
		logger.error('爬取文章数量: {}'.format(crawl_num))
		context = {}
		sg = SogouSpider()
		try:
			article_info = sg.crawl_keyword_articles(keyword=keyword, crawl_max=crawl_num)

			if not Word.objects.filter(keyword=keyword).count():
				Word.objects.update_or_create(keyword=keyword)

			update_article_database(article_info, keyword=keyword)

			context.update({'code': error_code.STATUS_OK, 'msg': len(article_info)})
		except Exception as e:
			logger.error("更新热词文章失败:%s" % e)

			context.update({'code': error_code.STATUS_ERROR, 'msg': '更新热词文章失败'})

		return JsonResponse(self.get_data(context))
