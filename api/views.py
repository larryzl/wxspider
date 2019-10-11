from django.shortcuts import HttpResponse
# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound
from web_admin.models import Article, WechatArticleKind
from .serializers import ArticleSerializers, DetailSerializers, TopicSerializers
import json


class P1(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'

    def paginate_queryset(self, queryset, request, view=None):
        request_data = json.dumps(request.data)
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.data.get('page', 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            self.display_page_controls = True
        self.request = request
        return list(self.page)

    def get_paginated_response(self, data):
        return Response(
            {
                'code': 0,
                'newsList': data
            }
        )


class ArticleView(APIView):
    def get(self, request):
        return Response({'code': 1, 'newsList': [], 'msg': 'method not allow'})

    def post(self, request, *args, **kwargs):
        data = request.data
        kind = data.get('chid')

        article_list = Article.objects.filter(kind__name=kind).order_by('-publish_time')

        p1 = P1()
        page_article_list = p1.paginate_queryset(queryset=article_list, request=request, view=self)
        serializer = ArticleSerializers(instance=page_article_list, many=True)

        return p1.get_paginated_response(serializer.data)


class DetailView(APIView):
    def get(self, request):
        return Response({'code': 1, 'newsDetail': [], 'msg': 'method not allow'})

    def post(self, request):
        id = request.data.get('id')
        try:
            article_detail = Article.objects.get(id=id)
        except:
            article_detail = None
            return Response({'code': 2, 'newsDetail': [], 'msg': 'article not found'})
        serializer = DetailSerializers(instance=article_detail, many=False)
        return HttpResponse(json.dumps(serializer.data, ensure_ascii=False))

class TopicView(APIView):
    def get(self,request):
        return Response({'code': 1, 'newsDetail': [], 'msg': 'method not allow'})

    def post(self, request):
        topic_list = WechatArticleKind.objects.all()
        serializer = TopicSerializers(instance=topic_list, many=True)
        return HttpResponse(json.dumps(serializer.data, ensure_ascii=False))
