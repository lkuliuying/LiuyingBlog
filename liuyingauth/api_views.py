"""
认证 / 用户中心 RESTful 接口。

- /api/auth/register/      POST 注册
- /api/auth/login/         POST 登录（账号 + 密码）→ access/refresh
- /api/auth/refresh/       POST 刷新 token（直接用 simplejwt 自带视图，url 里挂）
- /api/auth/captcha/       POST 发送邮箱验证码
- /api/auth/me/            GET / PATCH 当前用户
- /api/auth/me/password/   POST 改密码
- /api/auth/me/avatar/     POST 上传头像
- /api/auth/me/blogs/      GET 我发布的博客
- /api/auth/me/comments/   GET 我的评论
- /api/auth/me/likes/      GET 我点赞过的博客
- /api/auth/me/collections/ GET 我收藏的博客
"""
import random
import string

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from blog.models import Blog, BlogComment
from blog.serializers import BlogListSerializer, BlogCommentSerializer

from .models import CaptchaModel
from .serializers import (
    AvatarUploadSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
    UserBriefSerializer,
)


class CaptchaRateThrottle(AnonRateThrottle):
    """按 IP 限制验证码请求频率，防止邮件炸弹。"""
    scope = 'captcha'


class RegisterRateThrottle(AnonRateThrottle):
    """按 IP 限制注册尝试频率，防止验证码爆破。"""
    scope = 'register'


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserBriefSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({
            'access': serializer.validated_data['access'],
            'refresh': serializer.validated_data['refresh'],
            'user': UserBriefSerializer(serializer.validated_data['user']).data,
        })


class CaptchaView(APIView):
    """发送邮件验证码。

    频控三道闸：
    1) 同一邮箱 60s 内不能重复发（按 last_sent_at）；
    2) 同一邮箱 5 分钟内验证码不重新生成（重发只是把当前码再发一次）；
    3) 同一 IP 5 次/分钟（CaptchaRateThrottle）。
    """
    permission_classes = [AllowAny]
    throttle_classes = [CaptchaRateThrottle]

    def post(self, request):
        email = request.data.get('email') or request.query_params.get('email')
        if not email:
            return Response({'detail': '邮箱不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        with transaction.atomic():
            record = (
                CaptchaModel.objects
                .select_for_update()
                .filter(email=email)
                .first()
            )

            if record:
                # 60s 重发节流，按最近一次发送时间判断
                if (now - record.last_sent_at).total_seconds() < 60:
                    return Response(
                        {'detail': '验证码发送太频繁，请 60 秒后再试'},
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                    )
                # 5 分钟内复用同一验证码；过期则生成新的并重置失败计数
                if (now - record.created_time).total_seconds() > 5 * 60:
                    record.captcha = ''.join(random.choices(string.digits, k=6))
                    record.created_time = now
                    record.failed_attempts = 0
                record.last_sent_at = now
                record.save()
                captcha = record.captcha
            else:
                captcha = ''.join(random.choices(string.digits, k=6))
                CaptchaModel.objects.create(
                    email=email,
                    captcha=captcha,
                    last_sent_at=now,
                )

        try:
            plain_message = (
                f'您的流萤博客注册验证码是：{captcha}\n'
                '验证码 5 分钟内有效，请勿转发或告知他人。'
            )
            html_message = render_to_string(
                'liuyingauth/emails/registration_captcha.html',
                {'captcha': captcha},
            )
            send_mail(
                subject='流萤博客注册验证码',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
                html_message=html_message,
            )
        except Exception as exc:  # noqa: BLE001 — 邮件失败原因要回给前端
            return Response({'detail': f'邮件发送失败：{exc}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'detail': '验证码发送成功'})


class MeView(APIView):
    """当前用户信息（含统计）+ 修改用户名/邮箱。"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'user': UserBriefSerializer(user).data,
            'stats': {
                'blogs': Blog.objects.filter(author=user).count(),
                'comments': BlogComment.objects.filter(author=user).count(),
                'likes': user.liked_blogs.count(),
                'collections': user.collected_blogs.count(),
            },
        })

    def patch(self, request):
        serializer = UpdateProfileSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserBriefSerializer(user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': '密码修改成功'})


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AvatarUploadSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        return Response({
            'avatar': profile.avatar.url if profile.avatar else '',
        })


# ==========================================
# "我的" 列表：复用 BlogListSerializer / BlogCommentSerializer
# ==========================================
class MyBlogsView(generics.ListAPIView):
    serializer_class = BlogListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Blog.objects.filter(author=self.request.user) \
            .select_related('author', 'category').order_by('-pub_time')


class MyCommentsView(generics.ListAPIView):
    serializer_class = BlogCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BlogComment.objects.filter(author=self.request.user) \
            .select_related('author', 'blog').order_by('-pub_time')


class MyLikesView(generics.ListAPIView):
    serializer_class = BlogListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.liked_blogs.select_related('author', 'category').order_by('-pub_time')


class MyCollectionsView(generics.ListAPIView):
    serializer_class = BlogListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.collected_blogs.select_related('author', 'category').order_by('-pub_time')
