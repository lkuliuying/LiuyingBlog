from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AdminBlogViewSet,
    AdminCategoryViewSet,
    AdminCommentViewSet,
    AdminLoginView,
    AdminMeView,
    AdminUserViewSet,
    DashboardView,
)


app_name = "adminapi"

router = SimpleRouter()
router.register("blogs", AdminBlogViewSet, basename="blog")
router.register("categories", AdminCategoryViewSet, basename="category")
router.register("comments", AdminCommentViewSet, basename="comment")
router.register("users", AdminUserViewSet, basename="user")

urlpatterns = [
    path("auth/login/", AdminLoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("auth/me/", AdminMeView.as_view(), name="me"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("", include(router.urls)),
]
