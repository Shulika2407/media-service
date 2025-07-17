from django.contrib.auth import get_user_model, authenticate
from django.template.context_processors import request
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from customer.models import Profile, Follow


class UserRegisterSerializers(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "username")
        extra_kwargs = {
            "password": {
                "write_only": True, "min_length": 5,
            },
            "email": {
                "required": True
            },
            "username": {
                "required": True,
                "min_length": 5,
            }
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "user_image")


class ProfileListSerializers(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ("id", "first_name", "last_name", "email", "user_image", "age")

    def get_email(self, obj):
        # obj тут - це екземпляр моделі Profile
        # Ми отримуємо доступ до пов'язаного користувача через obj.user
        return obj.user.email


class ProfileDetailSerializer(serializers.ModelSerializer):
    user = UserRegisterSerializers()

    class Meta:
        model = Profile
        fields = ("first_name", "last_name", "user", "user_image", "age")

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        profile_instance = super().update(instance, validated_data)
        profile_instance.save()
        if user_data:
            user_instance = instance.user
            user_serializer = UserRegisterSerializers(
                instance=user_instance,
                data=user_data,
                partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        return profile_instance


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"), style={"input_type": "password"}
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if user:
                if not user.is_active:
                    msg = _("User account is disabled.")
                    raise serializers.ValidationError(msg, code="authorization")
            else:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _("Must include 'email' and 'password'.")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class FollowCreateSerializer(serializers.ModelSerializer):
    email_to_follow = serializers.EmailField(write_only=True, required=True)
    following_profile = ProfileListSerializers(read_only=True, source="following.profile")

    class Meta:
        model = Follow
        fields = ("email_to_follow", "following_profile")
        read_only_fields = ("following", "followers")

    def validate(self, data):
        email_to_follow = data.get("email_to_follow")
        request_user = self.context["request"].user

        try:
            user_to_follow = get_user_model().objects.get(email=email_to_follow)

        except get_user_model().DoesNotExist:
            raise serializers.ValidationError({"email_to_follow": "User with this email does not exist."})

        if request_user == user_to_follow:
            raise serializers.ValidationError("A user cannot be signed to themselves.")

        if Follow.objects.filter(followers=request_user, following=user_to_follow).exists():
            raise serializers.ValidationError("You are already following this user.")

        data["user_to_follow_obj"] = user_to_follow
        return data

    def create(self, validated_data):
        user_to_follow = validated_data.pop("user_to_follow_obj")
        request_user = self.context["request"].user

        follow_instance = Follow.objects.create(followers=request_user,
                                                following=user_to_follow)
        return follow_instance


class FollowingListSerializer(serializers.ModelSerializer):
    user_profile = ProfileListSerializers(read_only=True, source="following.profile")

    class Meta:
        model = Follow
        fields = ("id", "user_profile", "created_at")


class FollowingDetailSerializer(serializers.ModelSerializer):
    user_profile = ProfileDetailSerializer(read_only=True, source="following.profile")
    class Meta:
        model = Follow
        fields = ("id", "user_profile", "created_at")


class FollowersListSerializer(serializers.ModelSerializer):
    """
        Серіалізатор для відображення списку користувачів,
        які підписані на поточного користувача (FOLLOWERS).
    """
    follower_user_profile = ProfileListSerializers(read_only=True, source="followers.profile")

    class Meta:
        model = Follow
        fields = ("id", "follower_user_profile", "created_at")
