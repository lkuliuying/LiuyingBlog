"""
博客模块的序列化器。

设计原则：
- 列表与详情拆开，列表只给摘要、详情才给完整 content
- is_liked / is_collected 这类"当前用户视角"字段从 context['request'].user 推导
- 创建博客的字段校验逻辑由 PubBlogForm 平移过来
"""
from django.utils.html import strip_tags
from rest_framework import serializers

from .models import Blog, BlogCategory, BlogComment


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'name']


class _AuthorMixin:
    """复用作者字段：username + 头像 url。"""

    def _author_payload(self, user):
        avatar_url = ''
        profile = getattr(user, 'profile', None)
        if profile and profile.avatar:
            avatar_url = profile.avatar.url
        return {
            'id': user.id,
            'username': user.username,
            'avatar': avatar_url,
        }


class BlogListSerializer(_AuthorMixin, serializers.ModelSerializer):
    """首页 / 搜索 / 个人中心列表用。"""
    author = serializers.SerializerMethodField()
    category = BlogCategorySerializer(read_only=True)
    summary = serializers.SerializerMethodField()
    first_image = serializers.CharField(read_only=True)
    total_likes = serializers.IntegerField(source='likes.count', read_only=True)
    total_collections = serializers.IntegerField(source='collections.count', read_only=True)

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'summary', 'first_image',
            'author', 'category', 'pub_time',
            'total_likes', 'total_collections',
        ]

    def get_author(self, obj):
        return self._author_payload(obj.author)

    def get_summary(self, obj):
        return strip_tags(obj.content or '')[:120]


class BlogDetailSerializer(_AuthorMixin, serializers.ModelSerializer):
    """博客详情用，多带 content / is_liked / is_collected。"""
    author = serializers.SerializerMethodField()
    category = BlogCategorySerializer(read_only=True)
    total_likes = serializers.IntegerField(source='likes.count', read_only=True)
    total_collections = serializers.IntegerField(source='collections.count', read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_collected = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'content', 'pub_time', 'updated_time',
            'author', 'category',
            'total_likes', 'total_collections',
            'is_liked', 'is_collected',
        ]

    def get_author(self, obj):
        return self._author_payload(obj.author)

    def _user(self):
        request = self.context.get('request')
        return request.user if request and request.user.is_authenticated else None

    def get_is_liked(self, obj):
        user = self._user()
        return bool(user and obj.likes.filter(pk=user.pk).exists())

    def get_is_collected(self, obj):
        user = self._user()
        return bool(user and obj.collections.filter(pk=user.pk).exists())


class BlogCreateSerializer(serializers.ModelSerializer):
    """发布博客（POST/PUT）。
    校验规则平移自原 blog/forms.py:PubBlogForm。
    """
    title = serializers.CharField(min_length=2, max_length=200, error_messages={
        'required': '标题不能为空',
        'min_length': '标题长度不能小于2',
        'max_length': '标题长度不能大于200',
    })
    content = serializers.CharField(min_length=10, error_messages={
        'required': '内容不能为空',
        'min_length': '内容长度不能小于10',
    })
    category = serializers.PrimaryKeyRelatedField(
        queryset=BlogCategory.objects.all(),
        error_messages={'required': '分类不能为空', 'does_not_exist': '分类不存在'},
    )

    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'category']
        read_only_fields = ['id']


class BlogCommentSerializer(_AuthorMixin, serializers.ModelSerializer):
    """评论。前端拿到嵌套 replies 直接渲染评论树。"""
    author = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    total_likes = serializers.IntegerField(source='likes.count', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = BlogComment
        fields = [
            'id', 'blog', 'content', 'pub_time', 'parent',
            'author', 'replies', 'total_likes', 'is_liked',
        ]
        read_only_fields = ['id', 'pub_time', 'author']
        extra_kwargs = {
            # 列表里 blog 是必填，但我们走 /api/comments/?blog=xx 查询，所以 GET 不强制
            'blog': {'required': True},
            'parent': {'required': False, 'allow_null': True},
        }

    def get_author(self, obj):
        return self._author_payload(obj.author)

    def get_replies(self, obj):
        # 仅顶层评论才递归展开 replies（避免重复序列化整棵树）
        if obj.parent_id is not None:
            return []
        children = obj.replies.all().order_by('pub_time')
        return BlogCommentSerializer(children, many=True, context=self.context).data

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(pk=request.user.pk).exists()
