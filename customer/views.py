from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework import views
from rest_framework.decorators import action
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from customer.permissions import IsOwner
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.settings import api_settings
from customer.models import Profile
from customer.serializers import (UserRegisterSerializers,
                                  ProfileListSerializers,
                                  ProfileDetailSerializer,
                                  ProfileImageSerializer,
                                  AuthTokenSerializer)


# Create your views here.


class CreateUserViews(generics.CreateAPIView):
    serializer_class = UserRegisterSerializers
    authentication_classes = ()
    permission_classes = (AllowAny,)


class ProfileViews(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet,
                   mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Profile.objects.select_related("user").order_by("id")
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwner)

    def get_queryset(self):
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        queryset = self.queryset

        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)
        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "first_name",
                type=str,
                description="Filter by first_name (ex ?first_name=Tester)",
                required=False,
            ),
            OpenApiParameter(
                "last_name",
                type=str,
                description="Filter by last_name"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "upload_image":
            return ProfileImageSerializer
        if self.action == "retrieve":
            return ProfileDetailSerializer
        return ProfileListSerializers

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsOwner],
    )
    def upload_image(self, request, pk=None):
        profile_image = self.get_object()
        serializer = self.get_serializer(profile_image, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileDetailSerializer
    permission_classes = (IsOwner,)

    def get_object(self):
        return self.request.user.profile

