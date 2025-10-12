"""
API URL configuration for teacher dashboard
"""

from django.urls import path
from . import api_views

urlpatterns = [
    # Dashboard & Verification
    path('dashboard/', api_views.TeacherDashboardView.as_view(), name='teacher_api_dashboard'),
    path('verification/', api_views.VerificationStatusView.as_view(), name='teacher_api_verification'),

    # Course Management
    path('courses/', api_views.TeacherCoursesView.as_view(), name='teacher_api_courses_list'),
    path('courses/create/', api_views.CourseCreateView.as_view(), name='teacher_api_course_create'),
    path('courses/<int:course_id>/', api_views.CourseDetailView.as_view(), name='teacher_api_course_detail'),
    path('courses/<int:course_id>/update/', api_views.CourseUpdateView.as_view(), name='teacher_api_course_update'),
    path('courses/<int:course_id>/delete/', api_views.CourseDeleteView.as_view(), name='teacher_api_course_delete'),
    path('courses/<int:course_id>/preview/', api_views.CoursePreviewView.as_view(), name='teacher_api_course_preview'),

    # Publishing
    path('courses/<int:course_id>/publish/', api_views.CoursePublishView.as_view(), name='teacher_api_course_publish'),
    path('courses/<int:course_id>/unpublish/', api_views.CourseUnpublishView.as_view(), name='teacher_api_course_unpublish'),

    # Analytics & Export
    path('courses/<int:course_id>/analytics/', api_views.CourseAnalyticsView.as_view(), name='teacher_api_course_analytics'),
    path('courses/export/', api_views.ExportCoursesView.as_view(), name='teacher_api_courses_export'),

    # Module Management
    path('courses/<int:course_id>/modules/', api_views.ModuleListCreateView.as_view(), name='teacher_api_modules'),
    path('courses/<int:course_id>/modules/<int:module_id>/', api_views.ModuleDetailView.as_view(), name='teacher_api_module_detail'),
    path('courses/<int:course_id>/modules/<int:module_id>/update/', api_views.ModuleUpdateView.as_view(), name='teacher_api_module_update'),
    path('courses/<int:course_id>/modules/<int:module_id>/delete/', api_views.ModuleDeleteView.as_view(), name='teacher_api_module_delete'),

    # Lesson Management
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/', api_views.LessonListCreateView.as_view(), name='teacher_api_lessons'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/', api_views.LessonDetailAPIView.as_view(), name='teacher_api_lesson_detail'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/update/', api_views.LessonUpdateView.as_view(), name='teacher_api_lesson_update'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/delete/', api_views.LessonDeleteView.as_view(), name='teacher_api_lesson_delete'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/preview/', api_views.LessonPreviewView.as_view(), name='teacher_api_lesson_preview'),

    # Discussion Board
    path('courses/<int:course_id>/discussions/', api_views.CourseDiscussionsView.as_view(), name='teacher_api_discussions'),
    path('courses/<int:course_id>/discussions/create/', api_views.DiscussionCreateView.as_view(), name='teacher_api_discussion_create'),
    path('courses/<int:course_id>/discussions/<int:post_id>/', api_views.DiscussionDetailView.as_view(), name='teacher_api_discussion_detail'),
    path('courses/<int:course_id>/discussions/<int:post_id>/replies/', api_views.DiscussionReplyView.as_view(), name='teacher_api_discussion_reply'),
    path('courses/<int:course_id>/discussions/<int:post_id>/edit/', api_views.DiscussionEditView.as_view(), name='teacher_api_discussion_edit'),
    path('courses/<int:course_id>/discussions/<int:post_id>/delete/', api_views.DiscussionDeleteView.as_view(), name='teacher_api_discussion_delete'),
    path('courses/<int:course_id>/discussions/<int:post_id>/pin/', api_views.DiscussionPinToggleView.as_view(), name='teacher_api_discussion_pin'),

    # Media Serving
    path('videos/<path:video_path>', api_views.serve_video, name='teacher_api_serve_video'),
]
