"""博客模块的 RESTful 路由。"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api_views

app_name = 'blog'

router = DefaultRouter()
router.register('blogs', api_views.BlogViewSet, basename='blog')
router.register('categories', api_views.BlogCategoryViewSet, basename='category')
router.register('comments', api_views.BlogCommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('uploads/editor/', api_views.EditorUploadView.as_view(), name='editor_upload'),
]
