"""项目根 URL：所有业务接口聚到 /api/，admin 与 media 保持原状。"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/admin/', include('adminapi.urls')),
    path('api/', include('blog.urls')),
    path('api/auth/', include('liuyingauth.urls')),
]

# 媒体文件：开发环境直接由 Django 托管；生产环境交给 Nginx
if settings.DEBUG:
    urlpatterns += [
        path('', RedirectView.as_view(url='http://localhost:5173/', permanent=False)),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
