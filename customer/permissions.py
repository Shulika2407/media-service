from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Доступ тільки якщо користувач — власник об'єкта
        return obj.user == request.user