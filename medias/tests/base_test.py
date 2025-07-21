# medias/tests/base_test.py
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient

from customer.models import Profile, Follow  # Додано імпорт Follow та Profile
from medias.models import Post, Like, Comments  # Додано імпорт моделей medias

USER_MODEL = get_user_model()


class MediasBaseTest(APITestCase):
    """
    Базовий клас для налаштування тестів медіа-сервісу.
    Містить базових користувачів та функцію для автентифікації.
    """

    def setUp(self):
        self.client = APIClient()

        # Створення користувачів
        self.user1 = USER_MODEL.objects.create_user(
            email="user1@example.com", password="password123", username="user1_test"
        )
        self.user2 = USER_MODEL.objects.create_user(
            email="user2@example.com", password="password123", username="user2_test"
        )
        self.user3 = USER_MODEL.objects.create_user(
            email="user3@example.com", password="password123", username="user3_test"
        )

        # Створення профілів для користувачів (важливо для __str__ методу Follow)
        Profile.objects.get_or_create(user=self.user1)
        Profile.objects.get_or_create(user=self.user2)
        Profile.objects.get_or_create(user=self.user3)

        # URL-и
        self.myposts_list_url = reverse("medias:my_post-list")
        self.following_posts_list_url = reverse("medias:following_post-list")
        self.likes_list_url = reverse("medias:likes_post-list")
        self.comments_list_url = reverse("medias:comments-list")

    def _authenticate_user(self, user):
        """Автентифікує клієнта для заданого користувача за допомогою JWT."""
        response = self.client.post(
            reverse("customer:token_obtain_pair"),
            {"email": user.email, "password": "password123"},
        )
        access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
