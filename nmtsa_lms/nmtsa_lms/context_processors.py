"""
Context processors for NMTSA LMS.
These add data to all template contexts automatically.
"""

from django.urls import resolve, reverse


def breadcrumbs(request):
    """
    Automatically generate breadcrumbs based on the current URL.
    
    Returns breadcrumbs list for use in templates:
    - Visual breadcrumbs component
    - Schema.org BreadcrumbList structured data
    """
    
    # Get current URL name
    try:
        url_name = resolve(request.path).url_name
    except:
        url_name = None
    
    # Build breadcrumbs based on URL
    crumbs = [{'name': 'Home', 'url': '/'}]
    
    # Student pages
    if request.path.startswith('/student/'):
        if 'catalog' in request.path or 'courses' in request.path:
            crumbs.append({'name': 'Courses', 'url': '/student/catalog/'})
            if '/student/catalog/' not in request.path:
                crumbs.append({'name': 'Course Details', 'url': None})
        elif 'dashboard' in request.path:
            crumbs.append({'name': 'My Dashboard', 'url': None})
        elif 'enrollment' in request.path:
            crumbs.append({'name': 'My Courses', 'url': None})
    
    # Teacher pages
    elif request.path.startswith('/teacher/'):
        crumbs.append({'name': 'Teacher', 'url': '/teacher/dashboard/'})
        if 'courses' in request.path:
            crumbs.append({'name': 'Courses', 'url': '/teacher/courses/'})
            if 'create' in request.path:
                crumbs.append({'name': 'Create Course', 'url': None})
            elif 'edit' in request.path:
                crumbs.append({'name': 'Edit Course', 'url': None})
        elif 'dashboard' in request.path:
            crumbs.append({'name': 'Dashboard', 'url': None})
    
    # Admin pages
    elif request.path.startswith('/admin-dash/'):
        crumbs.append({'name': 'Admin', 'url': '/admin-dash/'})
        if 'verify' in request.path:
            crumbs.append({'name': 'Verify Teachers', 'url': None})
        elif 'review' in request.path:
            crumbs.append({'name': 'Review Courses', 'url': None})
    
    # Auth pages
    elif request.path.startswith('/auth/'):
        if 'onboarding' in request.path:
            crumbs.append({'name': 'Onboarding', 'url': None})
        elif 'select-role' in request.path:
            crumbs.append({'name': 'Select Role', 'url': None})
    
    # Landing page (no additional breadcrumbs needed)
    elif request.path == '/':
        pass  # Just "Home"
    
    return {
        'breadcrumbs': crumbs
    }


def site_info(request):
    """
    Add site-wide information to all templates.
    """
    return {
        'SITE_NAME': 'NMTSA Learning',
        'SITE_TAGLINE': 'Neurologic Music Therapy Education',
        'SUPPORT_EMAIL': 'support@nmtsalearning.com',
        'CURRENT_YEAR': 2025,
    }
