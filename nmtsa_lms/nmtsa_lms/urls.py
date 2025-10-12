"""
URL configuration for nmtsa_lms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from lms.sitemaps import sitemaps
from . import views
from student_dash import views as student_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.index, name="landing"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),
    path("auth/", include('authentication.urls')),
    
    # Public course browsing (no authentication required)
    path("courses/", student_views.public_catalog, name="public_catalog"),
    path("courses/<slug:course_slug>/", student_views.public_course_detail, name="public_course_detail"),
    
    # Protected student, teacher, admin routes
    path("student/", include('student_dash.urls')),
    path("teacher/", include('teacher_dash.urls')),
    path("admin-dash/", include('admin_dash.urls')),
    path("lms/", include('lms.urls')),
    
    # SEO Files
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

# Media files URL patterns (for file uploads)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
