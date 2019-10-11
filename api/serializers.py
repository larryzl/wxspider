from web_admin.models import Article
from rest_framework import serializers
from django.utils import dateformat

# class ArticleSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = Article
#         fields = ['id', 'title', 'kind', 'comment_count', 'publish_time', 'avatar']
#         extra_kwargs = {'news_style': 1}
#

"""
"news_id":3,
            "news_title":"巩俐饰演的郎平造型有多像？看朱婷的表情就知道了",
            "news_style":3,
            "news_chid":2,
            "news_commont":200,
            "news_datetime":"2019-01-03",
            "news_icon":[
"""


class ArticleSerializers(serializers.Serializer):
    news_id = serializers.IntegerField(source='id')
    news_title = serializers.CharField(source='title', max_length=32)
    news_chid = serializers.CharField(source='kind.name', max_length=32)
    news_commont = serializers.IntegerField(source='comment_count')
    news_datetime = serializers.SerializerMethodField()
    news_icon = serializers.SerializerMethodField()
    news_style = serializers.SerializerMethodField()

    def get_news_datetime(self, row):
        return str(row.publish_time.strftime("%Y-%m-%d"))

    def get_news_icon(self, row):
        return ["http://192.168.8.24" + row.avatar]

    def get_news_style(self, row):
        return 2


class DetailSerializers(serializers.Serializer):
    news_title = serializers.CharField(source='title', max_length=32)
    news_content = serializers.SerializerMethodField()
    news_date = serializers.SerializerMethodField()

    def get_news_content(self, row):
        return str(row.content).replace('data-src=', 'src=')

    def get_news_date(self, row):
        return str(row.publish_time.strftime("%Y-%m-%d"))


class TopicSerializers(serializers.Serializer):
    lanmu_id = serializers.CharField(source='uuid', max_length=32)
    lanmu_name = serializers.CharField(source='name', max_length=32)
    lanmu_order = serializers.IntegerField(default=1)
    lanmu_menu = serializers.IntegerField(default=1)
    lanmu_custom = serializers.IntegerField(default=1)
    lanmu_json = serializers.CharField(default='', max_length=32)
