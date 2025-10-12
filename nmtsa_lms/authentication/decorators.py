from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


def login_required(view_func):
    """
    Decorator that requires user to be logged in via Auth0
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user'):
            messages.info(request, 'Please log in to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*roles):
    """
    Decorator that requires user to have one of the specified roles
    Usage: @role_required('student', 'teacher')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.session.get('user')

            if not user:
                messages.error(request, 'Please log in to access this page.')
                return redirect('login')

            user_role = user.get('role')
            if user_role not in roles:
                messages.error(request, f'This page is only accessible to {", ".join(roles)}.')
                return redirect('index')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def student_required(view_func):
    """
    Decorator that requires user to be a student
    """
    return role_required('student')(view_func)


def teacher_required(view_func):
    """
    Decorator that requires user to be a teacher
    """
    return role_required('teacher')(view_func)


def admin_required(view_func):
    """
    Decorator that requires user to be an admin
    Supports Django authentication (username/password) only
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check Django authentication (for username/password admins)
        if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'admin':
            # Ensure session is populated for compatibility
            if not request.session.get('user'):
                request.session['user'] = {
                    'role': 'admin',
                    'user_id': request.user.id,
                    'username': request.user.username,
                    'full_name': request.user.get_full_name(),
                    'email': request.user.email,
                    'onboarding_complete': True,
                }
            return view_func(request, *args, **kwargs)

        messages.error(request, 'Admin access required. Please log in with your admin credentials.')
        return redirect('admin_login')
    return wrapper


def teacher_verified_required(view_func):
    """
    Decorator that requires teacher to be verified by admin
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.session.get('user')

        if not user:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')

        if user.get('role') != 'teacher':
            messages.error(request, 'This page is only accessible to teachers.')
            return redirect('index')

        if user.get('verification_status') != 'approved':
            messages.warning(request, 'Your teacher account is pending verification. You will be notified once approved.')
            return redirect('teacher_dashboard')

        return view_func(request, *args, **kwargs)
    return wrapper


def onboarding_complete_required(view_func):
    """
    Decorator that requires user to have completed onboarding
    Redirects to onboarding if not complete
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.session.get('user')

        if not user:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')

        if not user.get('onboarding_complete'):
            messages.info(request, 'Please complete your profile setup first.')

            # Redirect based on role
            if not user.get('role'):
                return redirect('select_role')
            elif user.get('role') == 'teacher':
                return redirect('teacher_onboarding')
            elif user.get('role') == 'student':
                return redirect('student_onboarding')

        return view_func(request, *args, **kwargs)
    return wrapper


def optional_login(view_func):
    """
    Decorator that allows both authenticated and anonymous users to access views.
    Populates request with user info if available, but doesn't redirect if not logged in.
    Sets flags that templates can use to conditionally display content.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Set flags for templates and view logic
        session_user = request.session.get('user')
        request.is_authenticated_user = bool(session_user)
        request.user_role = session_user.get('role', None) if session_user else None
        request.user_id = session_user.get('user_id', None) if session_user else None
        
        return view_func(request, *args, **kwargs)
    return wrapper
