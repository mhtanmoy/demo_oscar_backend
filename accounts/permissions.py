from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrAuthenticated(BasePermission):
    message = "Only superuser can create Employee Category"

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.method in SAFE_METHODS
        if request.user.is_authenticated and request.user.is_superuser:
            return True