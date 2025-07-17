from django.shortcuts import render
from rest_framework import views
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from medias.serializers import PostFollowingSerializer, MyPostSerializer
from rest_framework import viewsets, mixins, status
from medias.models import Post
from rest_framework.decorators import action
from rest_framework.response import Response
from customer.permissions import IsOwner
from drf_spectacular.utils import extend_schema, OpenApiParameter
from customer.models import Follow, User


class MyPostView(viewsets.ModelViewSet):
    serializer_class = MyPostSerializer
    permission_classes = (IsOwner,)
    queryset = Post.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-created_at").distinct()

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsOwner],
    )
    def upload_image(self, request, pk=None):
        post_image = self.get_object()
        serializer = self.get_serializer(post_image, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):

        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this post.")
        instance.delete()


class FollowingPost(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = PostFollowingSerializer
    queryset = Post.objects.all()

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Post.objects.none()

        hashtags = self.request.query_params.get("hashtags")
        name_post = self.request.query_params.get("name_post")

        users_followed_by_me = Follow.objects.filter(
            followers=self.request.user
        ).values_list("following", flat=True)

        queryset = self.queryset.filter(user__in=users_followed_by_me)

        if hashtags:
            queryset = queryset.filter(hashtags__icontains=hashtags)

        if name_post:
            queryset = queryset.filter(name_post__icontains=name_post)

        return queryset.order_by("-created_at").distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "hashtags", type=str,
                description="Filter by hashtags (ex ?hashtags=#Tester)"
            ),
            OpenApiParameter(
                "name_post", type=str,
                description="Filter by name_post (ex ?name_post=Tester)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)





