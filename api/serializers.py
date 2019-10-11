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
    news_datetime = serializers.DateTimeField(source='publish_time')
    news_icon = serializers.SerializerMethodField()
    news_style = serializers.SerializerMethodField()

    def get_news_icon(self, row):
        return [row.avatar]

    def get_news_style(self, row):
        return 1


class DetailSerializers(serializers.Serializer):
    news_title = serializers.CharField(source='title', max_length=32)
    news_content = serializers.SerializerMethodField()
    news_date = serializers.SerializerMethodField()

    def get_news_content(self, row):
        return str(row.content)

    def get_news_date(self, row):
        return str(row.publish_time.strftime("%Y-%m-%d"))

class TopicSerializers(serializers.Serializer):
    lanmu_id = serializers.CharField(source='uuid',max_length=32)
    lanmu_name = serializers.CharField(source='name',max_length=32)
    # lanmu_order =
    # lanmu_menu =
    # lanmu_custom =
    # lanmu_json =

