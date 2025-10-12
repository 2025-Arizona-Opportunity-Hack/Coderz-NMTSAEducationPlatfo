from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='student_dashboard'),
    path('courses/', views.courses, name='student_courses'),
    path('catalog/', views.catalog, name='student_catalog'),
    # Course detail and enrollment
    path('courses/<slug:course_slug>/', views.course_detail, name='student_course_detail'),
    path('courses/<slug:course_slug>/enroll/', views.enroll_in_course, name='student_enroll'),
    # Checkout and payment
    path('courses/<slug:course_slug>/checkout/', views.checkout_course, name='student_checkout'),
    path('courses/<slug:course_slug>/process-payment/', views.process_checkout, name='student_process_checkout'),
    # PayPal payment endpoints
    path('courses/<slug:course_slug>/payment/create-order/', views.create_paypal_order, name='student_create_paypal_order'),
    path('courses/<slug:course_slug>/payment/capture-order/', views.capture_paypal_order, name='student_capture_paypal_order'),
    # Learning routes
    path('courses/<slug:course_slug>/learn/', views.learning, name='student_learning'),
    path('courses/<slug:course_slug>/modules/<slug:module_slug>/lessons/<slug:lesson_slug>/', views.lesson_view, name='student_lesson'),
    path('courses/<slug:course_slug>/modules/<slug:module_slug>/lessons/<slug:lesson_slug>/complete/', views.mark_lesson_complete, name='student_mark_lesson_complete'),
    # API endpoints
    path('api/save-video-progress/', views.save_video_progress, name='student_save_video_progress'),
    # Certificates
    path('courses/<slug:course_slug>/certificate/', views.certificate, name='student_certificate'),
    path('courses/<slug:course_slug>/certificate.pdf', views.certificate_pdf, name='student_certificate_pdf'),
    # Discussion board
    path('courses/<slug:course_slug>/discussions/', views.course_discussions, name='student_course_discussions'),
    path('courses/<slug:course_slug>/discussions/create/', views.discussion_create, name='student_discussion_create'),
    path('courses/<slug:course_slug>/discussions/<int:post_id>/', views.discussion_detail, name='student_discussion_detail'),
    path('courses/<slug:course_slug>/discussions/<int:post_id>/reply/', views.discussion_reply, name='student_discussion_reply'),
    path('courses/<slug:course_slug>/discussions/<int:post_id>/edit/', views.discussion_edit, name='student_discussion_edit'),
    path('courses/<slug:course_slug>/discussions/<int:post_id>/delete/', views.discussion_delete, name='student_discussion_delete'),
]
