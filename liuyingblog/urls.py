"""项目根 URL：所有业务接口统一在 /api/ 下，Django Admin 已移除，改由 admin-frontend (Vue) 承接。"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path('api/admin/', include('adminapi.urls')),
    path('api/', include('blog.urls')),
    path('api/auth/', include('liuyingauth.urls')),
]

# 媒体文件：开发环境直接由 Django 托管；生产环境交给 Nginx
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
