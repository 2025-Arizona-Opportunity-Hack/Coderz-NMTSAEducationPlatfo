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
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog
from lms.sitemaps import sitemaps
from . import views
from student_dash import views as student_views

# Non-i18n URLs (SEO, API endpoints that shouldn't have language prefix)
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # SEO Files (no language prefix for crawlers)
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    
    # Language switcher endpoint (no language prefix)
    path('i18n/', include('django.conf.urls.i18n')),
    
    # JavaScript translations catalog
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]

# Translatable URLs (with language prefix like /en/, /es/, /fr/)
urlpatterns += i18n_patterns(
    path("", views.index, name="landing"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),
    path("auth/", include('authentication.urls')),
    
    # Public course browsing (no authentication required)
    path("courses/", student_views.public_catalog, name="public_catalog"),
    path("browse-courses/", student_views.public_catalog, name="browse_courses"),  # Alias for backward compatibility
    path("courses/<slug:course_slug>/", student_views.public_course_detail, name="public_course_detail"),
    
    # Protected student, teacher, admin routes
    path("student/", include('student_dash.urls')),
    path("teacher/", include('teacher_dash.urls')),
    path("admin-dash/", include('admin_dash.urls')),
    path("lms/", include('lms.urls')),
    
    # Legal Pages
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_of_service, name='terms_of_service'),
    path('cookies/', views.cookie_policy, name='cookie_policy'),
    
    # Support Pages
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    
    prefix_default_language=True,  # Include /en/ for English too
)

# Media files URL patterns (for file uploads)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
