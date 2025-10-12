"""
Custom permission classes for teacher dashboard
"""

from rest_framework import permissions
from teacher_dash.models import Course, Module


class IsCourseOwner(permissions.BasePermission):
    """
    Permission class that checks if the user is the owner of the course
    Requires course_id in view kwargs
    """
    message = "You can only access your own courses."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        course_id = view.kwargs.get('course_id')
        if not course_id:
            return False

        # Check if course exists and belongs to the user
        return Course.objects.filter(
            id=course_id,
            published_by=request.user
        ).exists()

    def has_object_permission(self, request, view, obj):
        # For course objects
        if isinstance(obj, Course):
            return obj.published_by == request.user
        return False


class IsModuleOwner(permissions.BasePermission):
    """
    Permission class that checks if the user owns the course that the module belongs to
    Requires module_id and course_id in view kwargs
    """
    message = "You can only access modules from your own courses."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        course_id = view.kwargs.get('course_id')
        module_id = view.kwargs.get('module_id')

        if not course_id or not module_id:
            return False

        # Check if module belongs to a course owned by the user
        try:
            course = Course.objects.get(id=course_id, published_by=request.user)
            return course.modules.filter(id=module_id).exists()
        except Course.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        # For module objects
        if isinstance(obj, Module):
            # Get the course this module belongs to
            course = Course.objects.filter(
                modules=obj,
                published_by=request.user
            ).first()
            return course is not None
        return False


class IsLessonOwner(permissions.BasePermission):
    """
    Permission class that checks if the user owns the course that the lesson belongs to
    Requires lesson_id, module_id, and course_id in view kwargs
    """
    message = "You can only access lessons from your own courses."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        course_id = view.kwargs.get('course_id')
        module_id = view.kwargs.get('module_id')
        lesson_id = view.kwargs.get('lesson_id')

        if not course_id or not module_id or not lesson_id:
            return False

        # Check if lesson belongs to a module in a course owned by the user
        try:
            course = Course.objects.get(id=course_id, published_by=request.user)
            module = course.modules.filter(id=module_id).first()
            if module:
                return module.lessons.filter(id=lesson_id).exists()
            return False
        except Course.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        # For lesson objects
        from teacher_dash.models import Lesson
        if isinstance(obj, Lesson):
            # Get the course this lesson belongs to through module
            course = Course.objects.filter(
                modules__lessons=obj,
                published_by=request.user
            ).first()
            return course is not None
        return False


class IsLessonOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class for lesson preview that allows both course owners and admins
    This is used for lesson preview functionality where admins need access for course review
    """
    message = "You can only preview lessons from your own courses or as an admin."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Allow admins
        if hasattr(request.user, 'role') and request.user.role == 'admin':
            return True

        # Check if user owns the course
        course_id = view.kwargs.get('course_id')
        module_id = view.kwargs.get('module_id')
        lesson_id = view.kwargs.get('lesson_id')

        if not course_id or not module_id or not lesson_id:
            return False

        # Check if lesson belongs to a module in a course owned by the user
        try:
            course = Course.objects.get(id=course_id, published_by=request.user)
            module = course.modules.filter(id=module_id).first()
            if module:
                return module.lessons.filter(id=lesson_id).exists()
            return False
        except Course.DoesNotExist:
            return False
