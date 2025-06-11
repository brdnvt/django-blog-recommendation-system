import base64
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.test import APITestCase, force_authenticate
from webap.models import BlogPost
from webap.views import BlogPostViewSet
User = get_user_model()
class BlogPostTestCase(APITestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.username = "Тарас Шевченко"
        self.password = "Volya"
        self.user = User.objects.create_user(
            username=self.username, email="sheva@ua", password=self.password
        )
        self.post = BlogPost.objects.create(
            title="Мені 13й минало", text="Мені 13й минало", author=self.user
        )
    def test_blog_post_obtain_returns_200(self):
        auth_headers = {
            "HTTP_AUTHORIZATION": "Basic "
            + base64.b64encode(
                f"{self.username}:{self.password}".encode("utf-8")
            ).decode(),
        }
        response = self.client.post("/api/login/", **auth_headers)
        token = response.data["token"]
        test_post_id = self.post.id
        response = self.client.get(
            f"/api/posts/{test_post_id}/", headers={"Authorization": f"Token {token}"}
        )
        assert response.status_code == 200, "Response status code must be 200"
        assert (
            "title" in response.data and response.data["title"] == "Мені 13й минало"
        ), "Title must be the same as in setUp"
