from rest_framework import serializers

from medias.models import Post


class PostFollowingSerializer(serializers.ModelSerializer):
    username = serializers.SlugRelatedField(
        source='user', many=False, read_only=True, slug_field="username"
    )

    class Meta:
        model = Post
        fields = ("id", "username", "name_post", "hashtags", "text", "image_post", "created_at")
        read_only_fields = ("id", "created_at")


class MyPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "name_post", "hashtags", "text", "image_post", "created_at")
        read_only_fields = ("id", "created_at")

