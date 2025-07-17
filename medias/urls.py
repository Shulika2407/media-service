from medias.views import MyPostView, FollowingPost
from django.urls import path, include
from rest_framework import routers

app_name = "medias"

router = routers.DefaultRouter()
router.register("my_post", MyPostView, basename="my_post")
router.register("following_post", FollowingPost, basename="following_post")

urlpatterns = [
    path("", include(router.urls)),
]

