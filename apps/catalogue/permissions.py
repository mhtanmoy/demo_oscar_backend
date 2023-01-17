from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsDepoManager(BasePermission):
    message = "Only Depot manager or Superuser can update product approval"

    def has_permission(self, request, view):
        if request.user.employees.filter(employee_category__id = 1).exists() or request.user.is_superuser:
            return True