from django.conf import settings
from django.db import models
import os
import uuid
from django.utils.text import slugify
from customer.models import User, UserManager


def image_post(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name_post)}-{uuid.uuid4()}{extension}"
    return os.path.join("uploads/posts", filename)


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="The user who created the post.",
        related_name="posts",
    )
    name_post = models.CharField(max_length=55)
    hashtags = models.CharField(max_length=65, blank=True)
    text = models.CharField(max_length=100)
    image_post = models.ImageField(null=True, blank=True, upload_to=image_post)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post {self.name_post} from the {self.user.username}"


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
        help_text="user who liked",
    )
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Like from {self.user.username}"
            f" to the post {self.post.name_post}"
            f" ({self.post.user.username})"
        )

    class Meta:
        # Це гарантує унікальність пари (user, post)
        unique_together = ("user", "post")


class Comments(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="user who comments",
    )
    text_comment = models.CharField(max_length=100)
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Це гарантує унікальність пари (user, post)
        unique_together = ("user", "post")

    def __str__(self):
        return (
            f"Comments from {self.user.username}"
            f" to the post {self.post.name_post}"
            f" ({self.post.user.username})"
        )
