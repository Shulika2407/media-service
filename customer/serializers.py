from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from customer.models import Profile


class UserRegisterSerializers(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password")
        extra_kwargs = {
            "password": {
                "write_only": True, "min_length": 5, "required": False,
            },
            "email": {
                "required": False
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
        fields = ("username", "first_name", "last_name", "email", "user_image", "age")

    def get_email(self, obj):
        # obj тут - це екземпляр моделі Profile
        # Ми отримуємо доступ до пов'язаного користувача через obj.user
        return obj.user.email


class ProfileDetailSerializer(serializers.ModelSerializer):
    user = UserRegisterSerializers()

    class Meta:
        model = Profile
        fields = ("username", "first_name", "last_name", "user", "user_image", "age")


    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        profile_instance = super().update(instance, validated_data)
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
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    msg = _("User account is disabled.")
                    raise serializers.ValidationError(msg, code="authorization")
            else:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _("Must include 'username' and 'password'.")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["customer"] = user
        return attrs

