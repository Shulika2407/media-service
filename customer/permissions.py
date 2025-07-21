from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method in ["GET", "HEAD", "OPTIONS"]:  # permissions.SAFE_METHODS
            return True

        if hasattr(obj, "user") and obj.user == request.user:
            return True

        if hasattr(obj, "followers") and obj.followers == request.user:
            return True

        return False
