from rest_framework import serializers

from medias.models import Post, Like, Comments

class PostBaseSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        # Успадковані класи будуть змінювати цю частину
        model = Post
        fields = ("id", "likes_count", "comments_count", "name_post",
                  "hashtags", "text", "image_post", "created_at")
        read_only_fields = ("id", "likes_count", "comments_count", "created_at")

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()


class PostFollowingSerializer(PostBaseSerializer):
    username = serializers.SlugRelatedField(
        source='user', many=False, read_only=True, slug_field="username"
    )

    class Meta:
        model = Post
        fields = PostBaseSerializer.Meta.fields + ("username",)
        read_only_fields = PostBaseSerializer.Meta.read_only_fields + ("username",)


class MyPostSerializer(PostBaseSerializer):


    class Meta:
        model = Post
        fields = PostBaseSerializer.Meta.fields
        read_only_fields = PostBaseSerializer.Meta.read_only_fields


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


class CommentsSerializer(serializers.ModelSerializer):
    user_who_comments = serializers.SlugRelatedField(
        source='user', many=False, read_only=True, slug_field="username"
    )
    post_comments = PostFollowingSerializer(read_only=True, source="post")

    class Meta:
        model = Comments
        fields = ("id", "user_who_comments", "post_comments", "post", "text_comment" ,"created_at")
        read_only_fields = ("id", "post_comments", "created_at", "user_who_comments")

    def validate(self, data):

        if self.context['request'].method == 'POST':
            user = self.context['request'].user
            post = data.get('post')

            if Comments.objects.filter(user=user, post=post).exists():
                raise serializers.ValidationError("You have already comments this post.")
        return data