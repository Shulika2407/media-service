from customer.views import (CreateUserViews, ProfileViews,
                            CreateTokenView, ManageUserView)
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

app_name = "customer"

router = routers.DefaultRouter()
router.register('profiles', ProfileViews, basename="profile")

urlpatterns = [
    path("register/", CreateUserViews.as_view(), name="create"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    path("me/", ManageUserView.as_view(), name="me"),
    path("", include(router.urls)),
]
