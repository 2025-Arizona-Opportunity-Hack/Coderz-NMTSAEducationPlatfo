"""
Custom permission classes for student dashboard
"""

from rest_framework import permissions
from authentication.models import Enrollment


class IsEnrolledInCourse(permissions.BasePermission):
    """
    Permission class that checks if user is enrolled in the course
    Requires course_id in view kwargs
    """
    message = "You must be enrolled in this course to access this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Get course_id from URL kwargs
        course_id = view.kwargs.get('course_id')
        if not course_id:
            return False

        # Check if enrollment exists
        return Enrollment.objects.filter(
            user=request.user,
            course_id=course_id,
            is_active=True
        ).exists()


class CanAccessDiscussion(permissions.BasePermission):
    """
    Permission class that checks if user can access course discussions
    Users who are enrolled, or the course teacher, or admins can access
    """
    message = "You must be enrolled in this course to access discussions."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        course_id = view.kwargs.get('course_id')
        if not course_id:
            return False

        # Admins can access all discussions
        if hasattr(request.user, 'role') and request.user.role == 'admin':
            return True

        # Course teacher can access
        from teacher_dash.models import Course
        try:
            course = Course.objects.get(id=course_id)
            if course.published_by == request.user:
                return True
        except Course.DoesNotExist:
            return False

        # Students must be enrolled
        if hasattr(request.user, 'role') and request.user.role == 'student':
            return Enrollment.objects.filter(
                user=request.user,
                course_id=course_id,
                is_active=True
            ).exists()

        return False


class IsDiscussionAuthor(permissions.BasePermission):
    """
    Object-level permission to check if user is the author of the discussion post
    """
    message = "You can only edit or delete your own posts."

    def has_object_permission(self, request, view, obj):
        # Safe methods (GET, HEAD, OPTIONS) are allowed for any user who can access discussions
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the post author
        return obj.user == request.user
