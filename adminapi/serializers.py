from django.contrib.auth import authenticate, get_user_model
from django.utils.html import strip_tags
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from blog.models import Blog, BlogCategory, BlogComment
from blog.sanitizers import sanitize_html


User = get_user_model()


def avatar_url(user):
    profile = getattr(user, "profile", None)
    if profile and profile.avatar:
        return profile.avatar.url
    return ""


class AdminIdentitySerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "avatar",
            "is_staff",
            "is_superuser",
        ]

    def get_avatar(self, obj):
        return avatar_url(obj)


class AdminLoginSerializer(serializers.Serializer):
    account = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["account"],
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError({"detail": "账号或密码错误"})
        if not user.is_active:
            raise serializers.ValidationError({"detail": "该账号已被禁用"})
        if not user.is_staff:
            raise serializers.ValidationError({"detail": "该账号没有管理后台权限"})

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": AdminIdentitySerializer(user).data,
        }


class AdminCategorySerializer(serializers.ModelSerializer):
    blog_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = BlogCategory
        fields = ["id", "name", "blog_count"]

    def validate_name(self, value):
        value = value.strip()
        queryset = BlogCategory.objects.filter(name__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("该分类已存在")
        return value


class AdminBlogSerializer(serializers.ModelSerializer):
    author = AdminIdentitySerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        source="author",
        queryset=User.objects.all(),
        write_only=True,
        required=False,
    )
    category = AdminCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=BlogCategory.objects.all(),
        write_only=True,
    )
    summary = serializers.SerializerMethodField()
    total_likes = serializers.IntegerField(read_only=True, default=0)
    total_collections = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "content",
            "summary",
            "author",
            "author_id",
            "category",
            "category_id",
            "pub_time",
            "updated_time",
            "total_likes",
            "total_collections",
        ]
        read_only_fields = ["id", "pub_time", "updated_time"]

    def get_summary(self, obj):
        return strip_tags(obj.content or "")[:120]

    def validate_title(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("标题至少需要 2 个字符")
        return value

    def validate_content(self, value):
        # 管理后台编辑博客同样走净化，避免绕过前台校验注入 XSS
        cleaned = sanitize_html(value)
        if len(strip_tags(cleaned).strip()) < 10:
            raise serializers.ValidationError("正文至少需要 10 个字符")
        return cleaned

    def create(self, validated_data):
        validated_data.setdefault("author", self.context["request"].user)
        return super().create(validated_data)


class AdminCommentSerializer(serializers.ModelSerializer):
    author = AdminIdentitySerializer(read_only=True)
    blog_title = serializers.CharField(source="blog.title", read_only=True)
    parent_content = serializers.CharField(source="parent.content", read_only=True)
    total_likes = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = BlogComment
        fields = [
            "id",
            "blog",
            "blog_title",
            "author",
            "content",
            "parent",
            "parent_content",
            "pub_time",
            "total_likes",
        ]
        read_only_fields = [
            "id",
            "blog",
            "blog_title",
            "author",
            "parent",
            "parent_content",
            "pub_time",
            "total_likes",
        ]


class AdminUserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    blog_count = serializers.IntegerField(read_only=True, default=0)
    comment_count = serializers.IntegerField(read_only=True, default=0)
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "avatar",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
            "blog_count",
            "comment_count",
            "follower_count",
            "following_count",
        ]
        read_only_fields = [
            "id",
            "avatar",
            "is_superuser",
            "date_joined",
            "last_login",
            "blog_count",
            "comment_count",
            "follower_count",
            "following_count",
        ]

    def get_avatar(self, obj):
        return avatar_url(obj)

    def get_follower_count(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.followers.count() if profile else 0

    def get_following_count(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.following.count() if profile else 0

    def validate_username(self, value):
        value = value.strip()
        queryset = User.objects.filter(username=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("该用户名已存在")
        return value

    def validate_email(self, value):
        value = value.strip()
        if not value:
            return value
        queryset = User.objects.filter(email__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("该邮箱已被使用")
        return value

