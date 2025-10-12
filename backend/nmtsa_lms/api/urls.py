"""
API URL Configuration
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import auth, courses, dashboard, forum, profile, lessons, teacher, admin

app_name = 'api'

urlpatterns = [
    # ============================================================================
    # AUTHENTICATION ENDPOINTS
    # ============================================================================
    path('auth/admin/login', auth.AdminLoginView.as_view(), name='admin-login'),
    path('auth/oauth/signin', auth.OAuthSignInView.as_view(), name='oauth-signin'),
    path('auth/me', auth.CurrentUserView.as_view(), name='current-user'),
    path('auth/logout', auth.LogoutView.as_view(), name='logout'),
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token-refresh'),
    
    # ============================================================================
    # PROFILE & ONBOARDING ENDPOINTS
    # ============================================================================
    path('profile', profile.ProfileView.as_view(), name='profile'),
    path('onboarding/select-role', profile.SelectRoleView.as_view(), name='select-role'),
    path('onboarding/teacher', profile.TeacherOnboardingView.as_view(), name='teacher-onboarding'),
    path('onboarding/student', profile.StudentOnboardingView.as_view(), name='student-onboarding'),
    
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
    # LESSON ENDPOINTS
    # ============================================================================
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>', 
         lessons.LessonContentView.as_view(), name='lesson-content'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/complete', 
         lessons.MarkLessonCompleteView.as_view(), name='lesson-complete'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/video-progress', 
         lessons.UpdateVideoProgressView.as_view(), name='lesson-video-progress'),
    
    # ============================================================================
    # CERTIFICATE ENDPOINTS
    # ============================================================================
    path('certificates/<int:enrollment_id>', lessons.CertificateView.as_view(), name='certificate'),
    path('certificates/<int:enrollment_id>/pdf', lessons.CertificatePDFView.as_view(), name='certificate-pdf'),
    
    # ============================================================================
    # FORUM ENDPOINTS
    # ============================================================================
    path('forum/posts', forum.forum_posts_list, name='forum-posts'),
    path('forum/tags', forum.forum_tags, name='forum-tags'),
    path('forum/posts/<int:post_id>', forum.forum_post_detail, name='forum-post-detail'),
    path('forum/posts/<int:post_id>/comments', forum.forum_post_comments, name='forum-post-comments'),
    path('forum/posts/<int:post_id>/like', forum.forum_post_like, name='forum-post-like'),
    path('forum/comments/<int:comment_id>/like', forum.forum_comment_like, name='forum-comment-like'),
    
    # ============================================================================
    # TEACHER ENDPOINTS
    # ============================================================================
    # Dashboard
    path('teacher/dashboard', teacher.TeacherDashboardView.as_view(), name='teacher-dashboard'),
    path('teacher/verification', teacher.VerificationStatusView.as_view(), name='teacher-verification'),
    
    # Courses
    path('teacher/courses', teacher.TeacherCoursesView.as_view(), name='teacher-courses-list'),
    path('teacher/courses/create', teacher.CourseCreateView.as_view(), name='teacher-course-create'),
    path('teacher/courses/<int:course_id>', teacher.CourseDetailUpdateDeleteView.as_view(), name='teacher-course-detail'),
    path('teacher/courses/<int:course_id>/<str:action>', teacher.CoursePublishView.as_view(), name='teacher-course-publish'),
    path('teacher/courses/<int:course_id>/analytics', teacher.CourseAnalyticsView.as_view(), name='teacher-course-analytics'),
    
    # Modules
    path('teacher/courses/<int:course_id>/modules', teacher.CourseModulesView.as_view(), name='teacher-course-modules'),
    path('teacher/courses/<int:course_id>/modules/create', teacher.ModuleCreateView.as_view(), name='teacher-module-create'),
    path('teacher/modules/<int:module_id>', teacher.ModuleDetailUpdateDeleteView.as_view(), name='teacher-module-detail'),
    
    # Lessons
    path('teacher/modules/<int:module_id>/lessons', teacher.ModuleLessonsView.as_view(), name='teacher-module-lessons'),
    path('teacher/modules/<int:module_id>/lessons/create', teacher.LessonCreateView.as_view(), name='teacher-lesson-create'),
    path('teacher/lessons/<int:lesson_id>', teacher.LessonDetailUpdateDeleteView.as_view(), name='teacher-lesson-detail'),
    
    # ============================================================================
    # ADMIN ENDPOINTS
    # ============================================================================
    # Dashboard
    path('admin/dashboard', admin.AdminDashboardView.as_view(), name='admin-dashboard'),
    
    # User Management
    path('admin/users', admin.UserManagementView.as_view(), name='admin-users'),
    path('admin/users/<int:user_id>', admin.UserDetailView.as_view(), name='admin-user-detail'),
    
    # Teacher Verification
    path('admin/teacher-verifications', admin.TeacherVerificationListView.as_view(), name='admin-teacher-verifications'),
    path('admin/teacher-verifications/<int:teacher_id>/review', admin.TeacherVerificationActionView.as_view(), name='admin-teacher-verification-review'),
    
    # Course Review
    path('admin/course-reviews', admin.CourseReviewListView.as_view(), name='admin-course-reviews'),
    path('admin/course-reviews/<int:course_id>/review', admin.CourseReviewActionView.as_view(), name='admin-course-review-action'),
    
    # Course Management
    path('admin/courses', admin.CourseManagementView.as_view(), name='admin-courses'),
    path('admin/courses/<int:course_id>/status', admin.CourseStatusUpdateView.as_view(), name='admin-course-status'),
    
    # Enrollment Management
    path('admin/enrollments', admin.EnrollmentManagementView.as_view(), name='admin-enrollments'),
    
    # ============================================================================
    # APPLICATIONS ENDPOINTS (to be implemented)
    # ============================================================================
    # path('applications', applications.ApplicationListView.as_view()),
    # path('applications/<int:pk>', applications.ApplicationDetailView.as_view()),
]
