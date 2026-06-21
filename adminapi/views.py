from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from blog.models import Blog, BlogCategory, BlogComment

from .pagination import AdminPagination
from .serializers import (
    AdminBlogSerializer,
    AdminCategorySerializer,
    AdminCommentSerializer,
    AdminIdentitySerializer,
    AdminLoginSerializer,
    AdminUserSerializer,
)


User = get_user_model()


def parse_ids(request):
    ids = request.data.get("ids", [])
    if not isinstance(ids, list) or not ids:
        raise ValidationError({"ids": "请选择至少一条记录"})
    try:
        return [int(item) for item in ids]
    except (TypeError, ValueError):
        raise ValidationError({"ids": "记录 ID 格式不正确"})


class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class AdminMeView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(AdminIdentitySerializer(request.user).data)


class DashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.now().date()
        start_day = today - timedelta(days=6)
        start_time = datetime.combine(start_day, time.min)

        user_series = {
            str(row["day"]): row["count"]
            for row in User.objects.filter(date_joined__gte=start_time)
            .annotate(day=TruncDate("date_joined"))
            .values("day")
            .annotate(count=Count("id"))
        }
        blog_series = {
            str(row["day"]): row["count"]
            for row in Blog.objects.filter(pub_time__gte=start_time)
            .annotate(day=TruncDate("pub_time"))
            .values("day")
            .annotate(count=Count("id"))
        }
        comment_series = {
            str(row["day"]): row["count"]
            for row in BlogComment.objects.filter(pub_time__gte=start_time)
            .annotate(day=TruncDate("pub_time"))
            .values("day")
            .annotate(count=Count("id"))
        }

        trend = []
        for offset in range(7):
            day = start_day + timedelta(days=offset)
            key = str(day)
            trend.append(
                {
                    "date": key,
                    "users": user_series.get(key, 0),
                    "blogs": blog_series.get(key, 0),
                    "comments": comment_series.get(key, 0),
                }
            )

        recent_blogs = (
            Blog.objects.select_related("author", "category")
            .annotate(
                total_likes=Count("likes", distinct=True),
                total_collections=Count("collections", distinct=True),
            )
            .order_by("-pub_time")[:6]
        )
        recent_comments = (
            BlogComment.objects.select_related("author", "blog", "parent")
            .annotate(total_likes=Count("likes", distinct=True))
            .order_by("-pub_time")[:6]
        )

        return Response(
            {
                "totals": {
                    "users": User.objects.count(),
                    "blogs": Blog.objects.count(),
                    "comments": BlogComment.objects.count(),
                    "categories": BlogCategory.objects.count(),
                },
                "today": {
                    "users": User.objects.filter(date_joined__date=today).count(),
                    "blogs": Blog.objects.filter(pub_time__date=today).count(),
                    "comments": BlogComment.objects.filter(pub_time__date=today).count(),
                },
                "trend": trend,
                "recent_blogs": AdminBlogSerializer(recent_blogs, many=True).data,
                "recent_comments": AdminCommentSerializer(recent_comments, many=True).data,
            }
        )


class AdminBlogViewSet(viewsets.ModelViewSet):
    serializer_class = AdminBlogSerializer
    permission_classes = [IsAdminUser]
    pagination_class = AdminPagination

    def get_queryset(self):
        queryset = (
            Blog.objects.select_related("author", "category")
            .annotate(
                total_likes=Count("likes", distinct=True),
                total_collections=Count("collections", distinct=True),
            )
        )
        search = self.request.query_params.get("search", "").strip()
        category = self.request.query_params.get("category")
        author = self.request.query_params.get("author")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(content__icontains=search)
                | Q(author__username__icontains=search)
            )
        if category:
            queryset = queryset.filter(category_id=category)
        if author:
            queryset = queryset.filter(author_id=author)
        if date_from:
            queryset = queryset.filter(pub_time__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(pub_time__date__lte=date_to)

        ordering = self.request.query_params.get("ordering", "-pub_time")
        allowed = {"pub_time", "-pub_time", "updated_time", "-updated_time", "title", "-title"}
        return queryset.order_by(ordering if ordering in allowed else "-pub_time")

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request):
        ids = parse_ids(request)
        count = self.get_queryset().filter(pk__in=ids).count()
        self.get_queryset().filter(pk__in=ids).delete()
        return Response({"deleted": count})


class AdminCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = AdminCategorySerializer
    permission_classes = [IsAdminUser]
    pagination_class = None

    def get_queryset(self):
        return BlogCategory.objects.annotate(blog_count=Count("blog")).order_by("id")

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        if category.blog_set.exists():
            return Response(
                {"detail": "该分类下仍有博客，请先调整博客分类"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


class AdminCommentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AdminCommentSerializer
    permission_classes = [IsAdminUser]
    pagination_class = AdminPagination

    def get_queryset(self):
        queryset = (
            BlogComment.objects.select_related("author", "blog", "parent")
            .annotate(total_likes=Count("likes", distinct=True))
        )
        search = self.request.query_params.get("search", "").strip()
        blog = self.request.query_params.get("blog")
        author = self.request.query_params.get("author")
        if search:
            queryset = queryset.filter(
                Q(content__icontains=search)
                | Q(author__username__icontains=search)
                | Q(blog__title__icontains=search)
            )
        if blog:
            queryset = queryset.filter(blog_id=blog)
        if author:
            queryset = queryset.filter(author_id=author)
        return queryset.order_by("-pub_time")

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request):
        ids = parse_ids(request)
        count = self.get_queryset().filter(pk__in=ids).count()
        self.get_queryset().filter(pk__in=ids).delete()
        return Response({"deleted": count})


class AdminUserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]
    pagination_class = AdminPagination

    def get_queryset(self):
        queryset = User.objects.annotate(
            blog_count=Count("blog", distinct=True),
            comment_count=Count("blogcomment", distinct=True),
        )
        search = self.request.query_params.get("search", "").strip()
        role = self.request.query_params.get("role")
        active = self.request.query_params.get("active")
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) | Q(email__icontains=search)
            )
        if role == "staff":
            queryset = queryset.filter(is_staff=True)
        elif role == "user":
            queryset = queryset.filter(is_staff=False)
        if active in {"true", "false"}:
            queryset = queryset.filter(is_active=active == "true")
        return queryset.order_by("-date_joined")

    def perform_update(self, serializer):
        target = self.get_object()
        next_active = serializer.validated_data.get("is_active", target.is_active)
        next_staff = serializer.validated_data.get("is_staff", target.is_staff)

        if target.pk == self.request.user.pk and (not next_active or not next_staff):
            raise ValidationError({"detail": "不能禁用或移除自己的管理权限"})
        if next_staff != target.is_staff and not self.request.user.is_superuser:
            raise PermissionDenied("只有超级管理员可以调整后台权限")
        serializer.save()
