from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser, BaseUserManager
import os
import uuid
from django.utils.text import slugify

from media_service import settings


# Create your models here.


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = models.CharField(max_length=150, unique=True, blank=False, null=False)
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()


def user_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.user.username)}--{uuid.uuid4()}{extension}"
    return os.path.join("uploads/profile", filename)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    # username = models.CharField(max_length=65, unique=True)
    first_name = models.CharField(max_length=65, null=True, blank=True)
    last_name = models.CharField(max_length=65, null=True, blank=True)
    user_image = models.ImageField(null=True, blank=True, upload_to=user_image_file_path)
    age = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        # Повертаємо ім'я користувача профілю
        return self.user.username


class Follow(models.Model):
    followers = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                               related_name="follower_set")
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                               related_name="following_set")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("followers", "following")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.followers.profile.username} follows {self.following.profile.username}"
