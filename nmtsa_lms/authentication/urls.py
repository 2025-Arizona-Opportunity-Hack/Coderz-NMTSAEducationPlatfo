from django.urls import path
from . import views, admin_views

urlpatterns = [
    # OAuth-based user routes
    path('select-role/', views.select_role, name='select_role'),
    path('onboarding/teacher/', views.teacher_onboarding, name='teacher_onboarding'),
    path('onboarding/student/', views.student_onboarding, name='student_onboarding'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),

    # Admin username/password authentication
    path('admin-login/', admin_views.admin_login, name='admin_login'),
    path('admin-logout/', admin_views.admin_logout, name='admin_logout'),
]
