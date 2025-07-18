from rest_framework import serializers

from medias.models import Post, Like


class PostFollowingSerializer(serializers.ModelSerializer):
    username = serializers.SlugRelatedField(
        source='user', many=False, read_only=True, slug_field="username"
    )
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ("id", "username", "likes_count", "name_post",
                  "hashtags", "text", "image_post", "created_at")
        read_only_fields = ("id", "likes_count", "created_at")

    def get_likes_count(self, obj):
        return obj.likes.count()


class MyPostSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ("id", "name_post", "likes_count",
                  "hashtags", "text", "image_post", "created_at")
        read_only_fields = ("id", "likes_count", "created_at")

    def get_likes_count(self, obj):
        return obj.likes.count()



class LikeSerializer(serializers.ModelSerializer):
    user_who_like = serializers.SlugRelatedField(
        source='user', many=False, read_only=True, slug_field="username"
    )
    post_like = PostFollowingSerializer(read_only=True, source="post")

    class Meta:
        model = Like
        fields = ("id", "user_who_like", "post_like", "post", "created_at")
        read_only_fields = ("id", "post_like", "created_at", "user_who_like")

    def validate(self, data):

        if self.context['request'].method == 'POST':
            user = self.context['request'].user
            post = data.get('post')

            if Like.objects.filter(user=user, post=post).exists():
                raise serializers.ValidationError("You have already liked this post.")
        return data
