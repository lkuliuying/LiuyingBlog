from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from blog.models import Blog, BlogCategory


User = get_user_model()


class AdminApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="reader",
            password="test-password",
        )
        self.staff = User.objects.create_user(
            username="editor",
            password="test-password",
            is_staff=True,
        )
        self.superuser = User.objects.create_superuser(
            username="root",
            email="root@example.com",
            password="test-password",
        )
        self.category = BlogCategory.objects.create(name="Python")
        self.blog = Blog.objects.create(
            title="测试文章",
            content="<p>这是一篇用于管理后台测试的完整文章内容。</p>",
            author=self.user,
            category=self.category,
        )

    def test_normal_user_cannot_login_to_admin(self):
        response = self.client.post(
            "/api/admin/auth/login/",
            {"account": "reader", "password": "test-password"},
        )
        self.assertEqual(response.status_code, 400)

    def test_staff_can_login_and_view_dashboard(self):
        response = self.client.post(
            "/api/admin/auth/login/",
            {"account": "editor", "password": "test-password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        dashboard = self.client.get("/api/admin/dashboard/")
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.data["totals"]["blogs"], 1)
        self.assertEqual(len(dashboard.data["trend"]), 7)

    def test_staff_can_update_and_bulk_delete_blogs(self):
        self.client.force_authenticate(self.staff)
        response = self.client.patch(
            f"/api/admin/blogs/{self.blog.pk}/",
            {
                "title": "更新后的标题",
                "content": "<p>更新后的正文内容已经超过十个字符。</p>",
                "category_id": self.category.pk,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.title, "更新后的标题")

        response = self.client.post(
            "/api/admin/blogs/bulk-delete/",
            {"ids": [self.blog.pk]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Blog.objects.filter(pk=self.blog.pk).exists())

    def test_category_with_blogs_cannot_be_deleted(self):
        self.client.force_authenticate(self.staff)
        response = self.client.delete(f"/api/admin/categories/{self.category.pk}/")
        self.assertEqual(response.status_code, 400)

    def test_only_superuser_can_grant_staff_permission(self):
        self.client.force_authenticate(self.staff)
        response = self.client.patch(
            f"/api/admin/users/{self.user.pk}/",
            {"is_staff": True},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

        self.client.force_authenticate(self.superuser)
        response = self.client.patch(
            f"/api/admin/users/{self.user.pk}/",
            {"is_staff": True},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)

