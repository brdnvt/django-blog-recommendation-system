from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Дозволяє змінювати або видаляти об’єкт лише його власнику.
    Перегляд дозволено всім (даже не автентифікованим).
    """
    def has_object_permission(self, request, view, obj):
        # Дозволити читання для безпечних методів (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Редагувати/видаляти може лише власник
        return obj.author == request.user
