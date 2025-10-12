"""
API views for admin dashboard
Handles teacher verification, course review, and admin statistics
"""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView

from authentication.models import User, TeacherProfile
from teacher_dash.models import Course
from admin_dash.permissions import IsAdminUser
from .serializers import (
    AdminDashboardStatsSerializer,
    TeacherVerificationListSerializer,
    TeacherVerificationDetailSerializer,
    TeacherVerificationActionSerializer,
    CourseReviewListSerializer,
    CourseReviewDetailSerializer,
    CourseReviewActionSerializer,
)


class AdminDashboardView(APIView):
    """
    GET /api/v1/admin/dashboard/
    Returns admin dashboard statistics
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Calculate statistics
        pending_teachers = TeacherProfile.objects.filter(verification_status='pending').count()
        total_users = User.objects.count()
        total_teachers = User.objects.filter(role='teacher').count()
        total_students = User.objects.filter(role='student').count()
        pending_courses = Course.objects.filter(is_submitted_for_review=True).count()

        stats = {
            'pending_teachers': pending_teachers,
            'total_users': total_users,
            'total_teachers': total_teachers,
            'total_students': total_students,
            'pending_courses': pending_courses,
        }

        serializer = AdminDashboardStatsSerializer(stats)
        return Response(serializer.data)


class PendingTeachersView(ListAPIView):
    """
    GET /api/v1/admin/teachers/pending/
    Returns paginated list of pending teacher verifications
    """
    permission_classes = [IsAdminUser]
    serializer_class = TeacherVerificationListSerializer
    queryset = TeacherProfile.objects.filter(
        verification_status='pending'
    ).select_related('user').order_by('-created_at')


class TeacherDetailView(RetrieveAPIView):
    """
    GET /api/v1/admin/teachers/{teacher_id}/
    Returns detailed teacher profile information for review
    """
    permission_classes = [IsAdminUser]
    serializer_class = TeacherVerificationDetailSerializer
    queryset = TeacherProfile.objects.select_related('user', 'verified_by')
    lookup_url_kwarg = 'teacher_id'


class VerifyTeacherView(APIView):
    """
    POST /api/v1/admin/teachers/{teacher_id}/verify/
    Approve or reject a teacher application
    """
    permission_classes = [IsAdminUser]

    def post(self, request, teacher_id):
        teacher_profile = get_object_or_404(TeacherProfile, id=teacher_id)

        serializer = TeacherVerificationActionSerializer(data=request.data)
        if serializer.is_valid():
            action = serializer.validated_data['action']
            notes = serializer.validated_data.get('notes', '')

            if action == 'approve':
                teacher_profile.verification_status = 'approved'
                teacher_profile.verified_at = timezone.now()
                teacher_profile.verified_by = request.user
                teacher_profile.verification_notes = notes
                teacher_profile.save()

                message = f'Teacher {teacher_profile.user.get_full_name()} has been approved!'

            elif action == 'reject':
                teacher_profile.verification_status = 'rejected'
                teacher_profile.verification_notes = notes
                teacher_profile.save()

                message = f'Teacher {teacher_profile.user.get_full_name()} has been rejected.'

            return Response(
                {
                    'message': message,
                    'teacher_profile': TeacherVerificationDetailSerializer(
                        teacher_profile,
                        context={'request': request}
                    ).data
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CoursesForReviewView(ListAPIView):
    """
    GET /api/v1/admin/courses/review/
    Returns paginated list of courses submitted for review
    """
    permission_classes = [IsAdminUser]
    serializer_class = CourseReviewListSerializer
    queryset = Course.objects.filter(
        is_submitted_for_review=True
    ).select_related('published_by').prefetch_related('modules').order_by('-published_date')


class CourseReviewDetailView(RetrieveAPIView):
    """
    GET /api/v1/admin/courses/{course_id}/
    Returns detailed course information for admin review
    """
    permission_classes = [IsAdminUser]
    serializer_class = CourseReviewDetailSerializer
    queryset = Course.objects.prefetch_related(
        'modules',
        'modules__lessons'
    ).select_related('published_by')
    lookup_url_kwarg = 'course_id'


class ReviewCourseActionView(APIView):
    """
    POST /api/v1/admin/courses/{course_id}/review/
    Approve or reject a course submission
    """
    permission_classes = [IsAdminUser]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        serializer = CourseReviewActionSerializer(data=request.data)
        if serializer.is_valid():
            action = serializer.validated_data['action']
            feedback = serializer.validated_data.get('feedback', '').strip()

            if action == 'approve':
                course.is_published = True
                course.is_submitted_for_review = False
                course.admin_approved = True
                course.admin_review_feedback = feedback
                course.save(update_fields=[
                    'is_published',
                    'is_submitted_for_review',
                    'admin_approved',
                    'admin_review_feedback'
                ])
                message = f"Approved course '{course.title}'."

            elif action == 'reject':
                course.is_published = False
                course.is_submitted_for_review = False
                course.admin_approved = False
                course.admin_review_feedback = feedback
                course.save(update_fields=[
                    'is_published',
                    'is_submitted_for_review',
                    'admin_approved',
                    'admin_review_feedback'
                ])
                message = f"Sent course '{course.title}' back to draft."

            return Response(
                {
                    'message': message,
                    'course': CourseReviewDetailSerializer(course).data
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminCoursePreviewView(RetrieveAPIView):
    """
    GET /api/v1/admin/courses/{course_id}/preview/
    Returns full course structure for admin preview
    """
    permission_classes = [IsAdminUser]
    serializer_class = CourseReviewDetailSerializer
    queryset = Course.objects.prefetch_related(
        'modules',
        'modules__lessons',
        'modules__lessons__video',
        'modules__lessons__blog'
    ).select_related('published_by')
    lookup_url_kwarg = 'course_id'
