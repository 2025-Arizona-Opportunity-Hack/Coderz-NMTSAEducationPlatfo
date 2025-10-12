from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('verify-teachers/', views.verify_teachers, name='admin_verify_teachers'),
    path('verify-teacher/<int:teacher_id>/', views.verify_teacher_action, name='admin_verify_teacher_action'),
    path('courses/review/', views.review_courses, name='admin_review_courses'),
    path('courses/review/<int:course_id>/', views.review_course_action, name='admin_review_course_action'),
    path('courses/review/<int:course_id>/preview/', views.admin_course_preview, name='admin_course_preview'),
]
