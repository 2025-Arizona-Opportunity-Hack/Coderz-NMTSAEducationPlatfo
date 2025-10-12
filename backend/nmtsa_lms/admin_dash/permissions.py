"""
Custom permission classes for admin dashboard
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission class that allows access only to admin users
    Same as authentication.permissions.IsAdmin but kept separate for admin_dash app
    """
    message = "Administrator access required."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role == 'admin'
        )
