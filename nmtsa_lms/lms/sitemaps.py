"""
Sitemap generation for NMTSA Learning Platform.
Creates XML sitemaps for search engines with dynamic content.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from teacher_dash.models import Course
from authentication.models import TeacherProfile


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages."""
    priority = 0.8
    changefreq = 'weekly'
    
    def items(self):
        """Return list of static page URL names."""
        return [
            'landing',  # Homepage
            # Add other public static pages here
        ]
    
    def location(self, item):
        """Get URL for each item."""
        return reverse(item)


class CourseSitemap(Sitemap):
    """Sitemap for published courses."""
    changefreq = 'weekly'
    priority = 0.9
    
    def items(self):
        """Return all published, admin-approved courses."""
        return Course.objects.filter(
            is_published=True,
            admin_approved=True
        ).select_related('created_by').order_by('-created_at')
    
    def lastmod(self, obj):
        """Return last modification date."""
        return obj.updated_at if hasattr(obj, 'updated_at') else obj.created_at
    
    def location(self, obj):
        """Get URL for course detail page."""
        # Assuming you have a course detail URL pattern
        # Adjust this based on your actual URL structure
        return f'/courses/{obj.id}/'


class TeacherProfileSitemap(Sitemap):
    """Sitemap for approved teacher profiles (public)."""
    changefreq = 'monthly'
    priority = 0.6
    
    def items(self):
        """Return all approved teachers with public profiles."""
        return TeacherProfile.objects.filter(
            verification_status='approved'
        ).select_related('user').order_by('user__username')
    
    def lastmod(self, obj):
        """Return last modification date."""
        return obj.created_at
    
    def location(self, obj):
        """Get URL for teacher profile page."""
        # Assuming you have a teacher profile URL pattern
        # Adjust based on your actual URL structure
        return f'/teachers/{obj.user.username}/'


# Sitemap dictionary for django.contrib.sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'courses': CourseSitemap,
    'teachers': TeacherProfileSitemap,
}
