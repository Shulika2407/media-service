# medias/tests/test_following_post_view.py
from rest_framework import status
from customer.models import Follow
from medias.models import Post
from .base_test import MediasBaseTest


class FollowingPostTests(MediasBaseTest):
    """Тести для ViewSet FollowingPost."""

    def setUp(self):
        super().setUp()
        self._authenticate_user(self.user1) # Автентифікація user1

        # Пости для тестування підписок
        self.post_by_user2 = Post.objects.create(
            user=self.user2,
            name_post="Post from User2",
            hashtags="#user2 #content",
            text="User2's public content."
        )
        self.post_by_user3_1 = Post.objects.create(
            user=self.user3,
            name_post="Post by User3 One",
            hashtags="#user3",
            text="User3's content A."
        )
        self.post_by_user3_2 = Post.objects.create(
            user=self.user3,
            name_post="Post by User3 Two",
            hashtags="#example",
            text="User3's content B."
        )

    def test_list_following_posts_authenticated_no_follows(self):
        """Перевірка отримання постів підписок для автентифікованого користувача без підписок."""
        response = self.client.get(self.following_posts_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_list_following_posts_authenticated_with_follows(self):
        """Перевірка отримання постів підписок для автентифікованого користувача з підписками."""
        Follow.objects.create(followers=self.user1, following=self.user2)
        response = self.client.get(self.following_posts_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name_post"], self.post_by_user2.name_post)

    def test_list_following_posts_unauthenticated(self):
        """Перевірка, що неавтентифікований користувач не отримує пости підписок."""
        self.client.credentials() # Зняти автентифікацію
        response = self.client.get(self.following_posts_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK) # Дозволяє IsAuthenticatedOrReadOnly
        self.assertEqual(len(response.data), 0)

    def test_filter_by_hashtags(self):
        """Перевірка фільтрації постів підписок за хештегами."""
        Follow.objects.create(followers=self.user1, following=self.user2)
        Follow.objects.create(followers=self.user1, following=self.user3)

        url = f"{self.following_posts_list_url}?hashtags=user3"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # Тільки один пост user3 має #user3
        self.assertEqual(response.data[0]["name_post"], self.post_by_user3_1.name_post)

    def test_filter_by_name_post(self):
        """Перевірка фільтрації постів підписок за назвою посту."""
        Follow.objects.create(followers=self.user1, following=self.user3)
        url = f"{self.following_posts_list_url}?name_post=User3 One"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name_post"], self.post_by_user3_1.name_post)