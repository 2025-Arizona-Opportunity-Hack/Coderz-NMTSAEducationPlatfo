"""
API URL Configuration
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import auth, courses, dashboard

app_name = 'api'

urlpatterns = [
    # ============================================================================
    # AUTHENTICATION ENDPOINTS
    # ============================================================================
    path('auth/admin/login', auth.AdminLoginView.as_view(), name='admin-login'),
    path('auth/me', auth.CurrentUserView.as_view(), name='current-user'),
    path('auth/logout', auth.LogoutView.as_view(), name='logout'),
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token-refresh'),
    
    # ============================================================================
    # COURSE ENDPOINTS
    # ============================================================================
    path('courses', courses.CourseListView.as_view(), name='course-list'),
    path('courses/categories', courses.CategoryListView.as_view(), name='course-categories'),
    path('courses/featured', courses.FeaturedCoursesView.as_view(), name='featured-courses'),
    path('courses/<int:pk>', courses.CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:pk>/detail', courses.CourseFullDetailView.as_view(), name='course-full-detail'),
    path('courses/<int:pk>/enroll', courses.EnrollmentView.as_view(), name='course-enroll'),
    path('courses/<int:pk>/reviews', courses.CourseReviewsView.as_view(), name='course-reviews'),
    
    # ============================================================================
    # DASHBOARD ENDPOINTS
    # ============================================================================
    path('dashboard/stats', dashboard.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/enrollments', dashboard.DashboardEnrollmentsView.as_view(), name='dashboard-enrollments'),
    path('dashboard/continue-learning', dashboard.ContinueLearningView.as_view(), name='continue-learning'),
    path('dashboard/certificates', dashboard.CertificatesView.as_view(), name='certificates'),
    
    # ============================================================================
    # LESSON ENDPOINTS (to be implemented)
    # ============================================================================
    # path('courses/<int:course_id>/lessons/<int:lesson_id>', lessons.LessonContentView.as_view()),
    # path('courses/<int:course_id>/lessons/<int:lesson_id>/complete', lessons.MarkCompleteView.as_view()),
    # path('courses/<int:course_id>/lessons/<int:lesson_id>/progress', lessons.ProgressUpdateView.as_view()),
    
    # ============================================================================
    # FORUM ENDPOINTS (to be implemented)
    # ============================================================================
    # path('forum/posts', forum.PostListView.as_view()),
    # path('forum/posts/<int:pk>', forum.PostDetailView.as_view()),
    
    # ============================================================================
    # APPLICATIONS ENDPOINTS (to be implemented)
    # ============================================================================
    # path('applications', applications.ApplicationListView.as_view()),
    # path('applications/<int:pk>', applications.ApplicationDetailView.as_view()),
]
