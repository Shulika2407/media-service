from medias.views import MyPostView, FollowingPost, LikeViews, CommentsViews
from django.urls import path, include
from rest_framework import routers

app_name = "medias"

router = routers.DefaultRouter()
router.register("my_post", MyPostView, basename="my_post")
router.register("following_post", FollowingPost, basename="following_post")
router.register("likes_post", LikeViews, basename="likes_post")
router.register("comments", CommentsViews, basename="comments")

urlpatterns = [
    path("", include(router.urls)),
]
