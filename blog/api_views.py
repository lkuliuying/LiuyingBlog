"""
博客模块的 RESTful 接口。

资源：
- /api/blogs/                    GET 列表 / POST 创建
- /api/blogs/{id}/               GET 详情 / PUT / DELETE
- /api/blogs/{id}/like/          POST 切换点赞
- /api/blogs/{id}/collect/       POST 切换收藏
- /api/categories/               GET 分类列表
- /api/comments/                 GET（按 blog 过滤） / POST
- /api/comments/{id}/like/       POST 切换评论点赞
- /api/uploads/editor/           POST 富文本编辑器图片/视频上传
"""
import uuid

from django.core.files.storage import default_storage
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Blog, BlogCategory, BlogComment
from .serializers import (
    BlogCategorySerializer,
    BlogCommentSerializer,
    BlogCreateSerializer,
    BlogDetailSerializer,
    BlogListSerializer,
)


class IsAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    """写操作需要登录，且只能操作自己的资源。"""

    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return obj.author_id == request.user.id


class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.select_related('author', 'category').all()
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['pub_time', 'updated_time']
    ordering = ['-pub_time']

    def get_serializer_class(self):
        if self.action == 'list':
            return BlogListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return BlogCreateSerializer
        return BlogDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        # 创建后返回详情视角，前端可以直接拿到 author / category 完整字段
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)
        instance = write_serializer.instance
        read_serializer = BlogDetailSerializer(instance, context=self.get_serializer_context())
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        blog = self.get_object()
        if blog.likes.filter(pk=request.user.pk).exists():
            blog.likes.remove(request.user)
            is_liked = False
        else:
            blog.likes.add(request.user)
            is_liked = True
        return Response({
            'is_liked': is_liked,
            'total_likes': blog.likes.count(),
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def collect(self, request, pk=None):
        blog = self.get_object()
        if blog.collections.filter(pk=request.user.pk).exists():
            blog.collections.remove(request.user)
            is_collected = False
        else:
            blog.collections.add(request.user)
            is_collected = True
        return Response({
            'is_collected': is_collected,
            'total_collections': blog.collections.count(),
        })


class BlogCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None  # 分类不分页


class BlogCommentViewSet(viewsets.ModelViewSet):
    """
    评论列表 / 创建 / 删除（仅作者）。
    GET /api/comments/?blog=<blog_id> 返回该博客的全部评论（树状）。
    """
    serializer_class = BlogCommentSerializer
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = None  # 评论一次性给前端拼成树

    def get_queryset(self):
        qs = BlogComment.objects.select_related('author', 'blog').all()
        blog_id = self.request.query_params.get('blog')
        if blog_id:
            qs = qs.filter(blog_id=blog_id)
        if self.action == 'list':
            # 列表只给顶层评论，replies 由序列化器内部递归展开
            qs = qs.filter(parent__isnull=True)
        return qs.order_by('-pub_time')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        if comment.likes.filter(pk=request.user.pk).exists():
            comment.likes.remove(request.user)
            is_liked = False
        else:
            comment.likes.add(request.user)
            is_liked = True
        return Response({
            'is_liked': is_liked,
            'total_likes': comment.likes.count(),
        })


# ==========================================
# 富文本编辑器：图片/视频上传
# wangEditor v5 约定的返回格式：{errno: 0, data: {url, alt, href}}
# ==========================================
class EditorUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    ALLOWED_EXTS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'}
    ALLOWED_CONTENT_TYPES = {
        'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp',
    }
    MAX_SIZE = 10 * 1024 * 1024

    def post(self, request):
        upload = request.FILES.get('file')
        if not upload:
            return Response(
                {'errno': 1, 'message': '没有接收到图片文件'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ext = upload.name.rsplit('.', 1)[-1].lower() if '.' in upload.name else ''
        if ext not in self.ALLOWED_EXTS:
            return Response(
                {'errno': 1, 'message': f'不支持的图片格式：.{ext or "未知"}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if upload.content_type not in self.ALLOWED_CONTENT_TYPES:
            return Response(
                {'errno': 1, 'message': '文件内容不是受支持的图片格式'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if upload.size > self.MAX_SIZE:
            return Response(
                {'errno': 1, 'message': '图片大小不能超过 10MB'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_filename = f'{uuid.uuid4().hex}.{ext}'
        date_path = timezone.now().strftime('%Y/%m')
        saved_path = default_storage.save(
            f'upload/{date_path}/{new_filename}',
            upload,
        )
        return Response({
            'errno': 0,
            'data': {
                'url': default_storage.url(saved_path),
                'alt': upload.name,
                'href': '',
            },
        }, status=status.HTTP_201_CREATED)
