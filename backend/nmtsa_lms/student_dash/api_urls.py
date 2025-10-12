"""
API URL configuration for student dashboard
"""

from django.urls import path
from . import api_views

urlpatterns = [
    # Dashboard
    path('dashboard/', api_views.StudentDashboardView.as_view(), name='student_dashboard'),

    # Courses
    path('courses/', api_views.EnrolledCoursesView.as_view(), name='enrolled_courses'),
    path('catalog/', api_views.CourseCatalogView.as_view(), name='course_catalog'),
    path('courses/<int:course_id>/', api_views.CourseDetailView.as_view(), name='course_detail'),

    # Enrollment
    path('courses/<int:course_id>/enroll/', api_views.EnrollInCourseView.as_view(), name='enroll'),
    path('courses/<int:course_id>/checkout/', api_views.CheckoutView.as_view(), name='checkout'),
    path('courses/<int:course_id>/checkout/process/', api_views.ProcessCheckoutView.as_view(), name='process_checkout'),

    # Learning
    path('courses/<int:course_id>/learn/', api_views.LearningView.as_view(), name='learning'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/',
         api_views.LessonView.as_view(), name='lesson'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/complete/',
         api_views.MarkLessonCompleteView.as_view(), name='complete_lesson'),
    path('video-progress/', api_views.SaveVideoProgressView.as_view(), name='video_progress'),

    # Certificates
    path('courses/<int:course_id>/certificate/', api_views.CertificateView.as_view(), name='certificate'),
    path('courses/<int:course_id>/certificate/pdf/', api_views.CertificatePDFView.as_view(), name='certificate_pdf'),

    # Discussions
    path('courses/<int:course_id>/discussions/', api_views.CourseDiscussionsView.as_view(), name='discussions'),
    path('courses/<int:course_id>/discussions/create/', api_views.DiscussionCreateView.as_view(), name='discussion_create'),
    path('courses/<int:course_id>/discussions/<int:post_id>/', api_views.DiscussionDetailView.as_view(), name='discussion_detail'),
    path('courses/<int:course_id>/discussions/<int:post_id>/replies/', api_views.DiscussionReplyView.as_view(), name='discussion_reply'),
    path('courses/<int:course_id>/discussions/<int:post_id>/edit/', api_views.DiscussionEditView.as_view(), name='discussion_edit'),
    path('courses/<int:course_id>/discussions/<int:post_id>/delete/', api_views.DiscussionDeleteView.as_view(), name='discussion_delete'),
]
