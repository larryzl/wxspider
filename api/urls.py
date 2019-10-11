
from django.urls import re_path
from api.views import ArticleView, DetailView, TopicView

urlpatterns = [
    re_path(r'article/$', ArticleView.as_view()),
    re_path(r'detail/$', DetailView.as_view()),
    re_path(r'topic/$', TopicView.as_view())
    ]
