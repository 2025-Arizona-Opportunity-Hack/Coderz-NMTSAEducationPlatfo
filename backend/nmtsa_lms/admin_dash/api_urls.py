"""
API URL configuration for admin dashboard
"""

from django.urls import path
from . import api_views

urlpatterns = [
    # Dashboard
    path('dashboard/', api_views.AdminDashboardView.as_view(), name='admin_dashboard'),

    # Teacher verification
    path('teachers/pending/', api_views.PendingTeachersView.as_view(), name='pending_teachers'),
    path('teachers/<int:teacher_id>/', api_views.TeacherDetailView.as_view(), name='teacher_detail'),
    path('teachers/<int:teacher_id>/verify/', api_views.VerifyTeacherView.as_view(), name='verify_teacher'),

    # Course review
    path('courses/review/', api_views.CoursesForReviewView.as_view(), name='courses_review'),
    path('courses/<int:course_id>/', api_views.CourseReviewDetailView.as_view(), name='course_review_detail'),
    path('courses/<int:course_id>/review/', api_views.ReviewCourseActionView.as_view(), name='course_review_action'),
    path('courses/<int:course_id>/preview/', api_views.AdminCoursePreviewView.as_view(), name='course_preview'),
]
