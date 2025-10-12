"""
Custom permission classes for Django REST Framework
Role-based and conditional permissions for the NMTSA LMS API
"""

from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    """
    Permission class that allows access only to users with 'student' role
    """
    message = "You must be a student to access this resource."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role == 'student'
        )


class IsTeacher(permissions.BasePermission):
    """
    Permission class that allows access only to users with 'teacher' role
    """
    message = "You must be a teacher to access this resource."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role == 'teacher'
        )


class IsTeacherVerified(permissions.BasePermission):
    """
    Permission class that allows access only to verified teachers
    Teacher must have 'approved' verification status
    """
    message = "Your teacher profile must be verified to access this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if not hasattr(request.user, 'role') or request.user.role != 'teacher':
            return False

        # Check if teacher has approved profile
        if hasattr(request.user, 'teacher_profile'):
            return request.user.teacher_profile.verification_status == 'approved'

        return False


class IsAdmin(permissions.BasePermission):
    """
    Permission class that allows access only to users with 'admin' role
    """
    message = "You must be an administrator to access this resource."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role == 'admin'
        )


class IsOnboardingComplete(permissions.BasePermission):
    """
    Permission class that requires user to have completed onboarding
    """
    message = "You must complete your profile setup before accessing this resource."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'onboarding_complete') and
            request.user.onboarding_complete
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it
    Read permissions are allowed to any authenticated user
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user
