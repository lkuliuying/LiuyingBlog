from rest_framework import serializers
from .models import Blog

class BlogSerializer(serializers.ModelSerializer):
    # 把数据库里的作者名字转成字符串（否则接口里会只显示作者ID）
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'pub_time', 'author_name'] # 接口里只暴露这5个字段