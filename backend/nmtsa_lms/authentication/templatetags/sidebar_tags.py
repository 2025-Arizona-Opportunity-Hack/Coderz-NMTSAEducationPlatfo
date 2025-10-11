"""
Custom template tags for rendering sidebars based on user role
"""
from django import template

register = template.Library()


@register.inclusion_tag('components/sidebar.html')
def sidebar(active, role):
    """
    Render a sidebar based on the user's role

    Args:
        active: The currently active menu item key
        role: The user's role ('admin', 'teacher', 'student')

    Returns:
        Context dict with 'items' and 'active' for the sidebar template
    """

    # Define sidebar items based on role
    if role == 'admin':
        items = [
            {'key': 'dashboard', 'label': 'Dashboard', 'url': '/admin-dash/', 'icon': 'home'},
            {'key': 'verify', 'label': 'Verify Teachers', 'url': '/admin-dash/verify-teachers/', 'icon': 'users'},
            {'key': 'settings', 'label': 'Settings', 'url': '/auth/profile/settings/', 'icon': 'settings'},
        ]
    elif role == 'teacher':
        items = [
            {'key': 'dashboard', 'label': 'Dashboard', 'url': '/teacher/', 'icon': 'home'},
            {'key': 'courses', 'label': 'My Courses', 'url': '/teacher/courses/', 'icon': 'book'},
            {'key': 'create', 'label': 'Create Course', 'url': '/teacher/courses/create/', 'icon': 'plus'},
            {'key': 'settings', 'label': 'Settings', 'url': '/auth/profile/settings/', 'icon': 'settings'},
        ]
    elif role == 'student':
        items = [
            {'key': 'dashboard', 'label': 'Dashboard', 'url': '/student/', 'icon': 'home'},
            {'key': 'courses', 'label': 'My Courses', 'url': '/student/courses/', 'icon': 'book'},
            {'key': 'catalog', 'label': 'Browse Catalog', 'url': '/student/catalog/', 'icon': 'search'},
            {'key': 'settings', 'label': 'Settings', 'url': '/auth/profile/settings/', 'icon': 'settings'},
        ]
    else:
        # Default empty sidebar
        items = []

    return {
        'items': items,
        'active': active,
    }
