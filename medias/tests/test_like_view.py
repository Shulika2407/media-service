from rest_framework import status
from django.urls import reverse

from medias.models import Like, Post
from .base_test import MediasBaseTest


class LikeViewsTests(MediasBaseTest):
    """Тести для ViewSet LikeViews."""

    def setUp(self):
        super().setUp()
        self._authenticate_user(self.user1)

        # Створення постів для тестування лайків
        self.post_by_user2 = Post.objects.create(
            user=self.user2,
            name_post="Post to Like",
            hashtags="#likeable",
            text="This post can be liked.",
        )
        self.post_by_user3 = Post.objects.create(
            user=self.user3,
            name_post="Another Post to Like",
            hashtags="#likeable_too",
            text="This one too.",
        )

    def test_create_like(self):
        """Перевірка створення лайку."""
        payload = {"post": self.post_by_user2.id}
        response = self.client.post(self.likes_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)
        new_like = Like.objects.first()
        self.assertEqual(new_like.user, self.user1)
        self.assertEqual(new_like.post, self.post_by_user2)

    def test_create_duplicate_like_forbidden(self):
        """Перевірка, що не можна поставити лайк двічі на один пост."""
        Like.objects.create(user=self.user1, post=self.post_by_user2)  # Створюємо лайк
        payload = {"post": self.post_by_user2.id}
        response = self.client.post(self.likes_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("non_field_errors", response.data)
        self.assertTrue(
            any(
                "You have already liked this post." in str(error)
                for error in response.data["non_field_errors"]
            )
        )
        self.assertEqual(Like.objects.count(), 1)  # Кількість лайків не змінилась

    def test_list_my_likes(self):
        """Перевірка отримання власних лайків."""
        Like.objects.create(user=self.user1, post=self.post_by_user2)
        Like.objects.create(user=self.user1, post=self.post_by_user3)
        Like.objects.create(user=self.user2, post=self.post_by_user2)  # Лайк від user2
        response = self.client.get(self.likes_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Припускаючи, що ваш серіалізатор повертає 'post' як словник з 'id'
        self.assertTrue(
            any(like.get("post") == self.post_by_user2.id for like in response.data)
        )
        self.assertTrue(
            any(like.get("post") == self.post_by_user3.id for like in response.data)
        )
        # Перевірка, що лайки інших користувачів не включені до списку
        self.assertFalse(
            any(like.get("user") == self.user2.id for like in response.data)
        )

    def test_delete_my_like(self):
        """Перевірка видалення власного лайку."""
        like = Like.objects.create(user=self.user1, post=self.post_by_user2)
        url = reverse("medias:likes_post-detail", args=[like.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Like.objects.count(), 0)
        self.assertFalse(Like.objects.filter(id=like.id).exists())

    def test_delete_other_user_like_forbidden(self):
        """Перевірка, що не можна видалити лайк іншого користувача."""
        like_by_user1 = Like.objects.create(user=self.user1, post=self.post_by_user2)

        url_to_delete = reverse("medias:likes_post-detail", args=[like_by_user1.id])
        self._authenticate_user(self.user2)

        response = self.client.delete(url_to_delete)  # Використовуємо url_to_delete тут
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )  # Очікуємо 404

        self.assertTrue(Like.objects.filter(id=like_by_user1.id).exists())
        self.assertEqual(Like.objects.count(), 1)
