from typing import Collection, Any
from rest_framework.response import Response
from rest_framework import status

  
def has_permission(
        group_name: Collection[str] = None,
        permissions: Collection[str] = None,
        is_admin: bool = None,
) -> Any:
    def decorator(function):
        def wrapper(self, request, *args, **kwargs):
            if not request.user.is_superuser:
                if is_admin is not None:
                    if not request.user.is_admin:
                        return Response(
                            "You are not a admin user.", status=status.HTTP_400_BAD_REQUEST)
                if group_name is not None:
                    group_name_list = group_name
                    if type(group_name) == str:
                        group_name_list = [group_name]
                    if not request.user.groups.filter(
                            name__in=group_name_list).exists():
                        return Response(
                            "You do not have permission.", status=status.HTTP_400_BAD_REQUEST)
                if permissions is not None:
                    permissions_list = permissions
                    if type(permissions) == str:
                        permissions_list = [permissions]
                    if not request.user.has_perms(permissions_list):
                        return Response(
                            "You do not have permission.", status=status.HTTP_400_BAD_REQUEST)
            return function(self, request, *args, **kwargs)
        return wrapper
    return decorator