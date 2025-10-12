"""
API URL configuration for authentication app
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views

urlpatterns = [
    # JWT token management
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', api_views.CurrentUserView.as_view(), name='current_user'),
    path('logout/', api_views.LogoutView.as_view(), name='logout'),

    # Onboarding
    path('select-role/', api_views.SelectRoleView.as_view(), name='select_role'),
    path('onboarding/teacher/', api_views.TeacherOnboardingView.as_view(), name='teacher_onboarding'),
    path('onboarding/student/', api_views.StudentOnboardingView.as_view(), name='student_onboarding'),
    path('profile/', api_views.ProfileSettingsView.as_view(), name='profile_settings'),

    # Admin authentication
    path('admin/login/', api_views.AdminLoginView.as_view(), name='admin_login'),
    path('admin/logout/', api_views.AdminLogoutView.as_view(), name='admin_logout'),
]
