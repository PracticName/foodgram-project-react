from djoser.permissions import CurrentUserOrAdminOrReadOnly
from rest_framework import permissions


class CurrentUserOrAdminOrReaOnly(CurrentUserOrAdminOrReadOnly):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS)
