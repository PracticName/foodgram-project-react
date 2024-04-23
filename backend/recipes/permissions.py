from djoser.permissions import CurrentUserOrAdminOrReadOnly
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает анонимному пользователю только безопасные запросы.

    Предоставляет права на осуществление запросов
    только суперпользователю или админу.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated and request.user.is_admin))


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Предоставляет доступ к объекту только автору.

    Разрешает анонимному и аутентифицированному пользователю
    только безопасные запросы.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class CurrentUserOrAdminOrReaOnly(CurrentUserOrAdminOrReadOnly):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS)
