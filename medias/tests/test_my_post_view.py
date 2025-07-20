# medias/tests/test_my_post_view.py
from rest_framework import status
from django.urls import reverse

from medias.models import Post
from .base_test import MediasBaseTest # Імпорт базового класу


class MyPostViewTests(MediasBaseTest):
    """Тести для ViewSet MyPostView."""

    def setUp(self):
        super().setUp()
        self._authenticate_user(self.user1) # Автентифікація user1 за замовчуванням для цих тестів

        # Створення постів для user1
        self.post1_user1 = Post.objects.create(
            user=self.user1,
            name_post="Test Post 1 by User1",
            hashtags="#test1",
            text="Content 1"
        )
        self.post2_user1 = Post.objects.create(
            user=self.user1,
            name_post="Test Post 2 by User1",
            hashtags="#test2",
            text="Content 2"
        )
        # Пост для іншого користувача, щоб перевірити дозволи
        self.post_user2 = Post.objects.create(
            user=self.user2,
            name_post="Post by User2",
            hashtags="#other",
            text="Content other"
        )

    def test_list_my_posts_authenticated(self):
        """Перевірка отримання тільки власних постів для автентифікованого користувача."""
        response = self.client.get(self.myposts_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) # user1 має 2 пости
        print("Response data for test_list_my_posts_authenticated:", response.data)
        self.assertEqual(response.data[0]['name_post'], self.post2_user1.name_post) # Order by -created_at
        self.assertEqual(response.data[1]['name_post'], self.post1_user1.name_post)

    def test_list_my_posts_unauthenticated(self):
        """Перевірка, що неавтентифікований користувач не може отримати пости."""
        self.client.logout()
        response = self.client.get(self.myposts_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_create_post(self):
        """Перевірка створення посту автентифікованим користувачем."""
        payload = {
            "name_post": "New Post by User1",
            "hashtags": "#new",
            "text": "This is a brand new post."
        }
        response = self.client.post(self.myposts_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 4) # 3 існуючих + 1 новий
        new_post = Post.objects.get(name_post="New Post by User1")
        self.assertEqual(new_post.user, self.user1)

    def test_retrieve_my_post(self):
        """Перевірка отримання власного посту."""
        url = reverse("medias:my_post-detail", args=[self.post1_user1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name_post"], self.post1_user1.name_post)

    def test_retrieve_other_user_post_forbidden(self):
        """Перевірка, що не можна отримати пост іншого користувача."""
        url = reverse("medias:my_post-detail", args=[self.post_user2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) # Завдяки get_queryset фільтрації по user

    def test_update_my_post(self):
        """Перевірка оновлення власного посту."""
        url = reverse("medias:my_post-detail", args=[self.post1_user1.id])
        payload = {"name_post": "Updated Post Name"}
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post1_user1.refresh_from_db()
        self.assertEqual(self.post1_user1.name_post, "Updated Post Name")

    def test_update_other_user_post_forbidden(self):
        """Перевірка, що не можна оновити пост іншого користувача."""
        url = reverse("medias:my_post-detail", args=[self.post_user2.id])
        payload = {"name_post": "Attempted Update"}
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_my_post(self):
        """Перевірка видалення власного посту."""
        url = reverse("medias:my_post-detail", args=[self.post1_user1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 2) # 3 - 1 = 2
        self.assertFalse(Post.objects.filter(id=self.post1_user1.id).exists())

    def test_delete_other_user_post_forbidden(self):
        """Перевірка, що не можна видалити пост іншого користувача."""
        url = reverse("medias:my_post-detail", args=[self.post_user2.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)