"""认证模块路由。"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import api_views

app_name = 'liuyingauth'

urlpatterns = [
    path('register/', api_views.RegisterView.as_view(), name='register'),
    path('login/', api_views.LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('captcha/', api_views.CaptchaView.as_view(), name='captcha'),

    # 当前用户
    path('me/', api_views.MeView.as_view(), name='me'),
    path('me/password/', api_views.ChangePasswordView.as_view(), name='change_password'),
    path('me/avatar/', api_views.AvatarUploadView.as_view(), name='upload_avatar'),
    path('me/blogs/', api_views.MyBlogsView.as_view(), name='my_blogs'),
    path('me/comments/', api_views.MyCommentsView.as_view(), name='my_comments'),
    path('me/likes/', api_views.MyLikesView.as_view(), name='my_likes'),
    path('me/collections/', api_views.MyCollectionsView.as_view(), name='my_collections'),
]
