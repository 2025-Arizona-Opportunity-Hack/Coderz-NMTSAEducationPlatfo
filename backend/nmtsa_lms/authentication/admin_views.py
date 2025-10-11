"""
Admin-specific authentication views
Username/password authentication for admin users only
"""
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache


@never_cache
def admin_login(request):
    """
    Admin login view using Django's built-in authentication
    Only for users with role='admin'
    """
    # If already logged in as admin, redirect to dashboard
    if request.user.is_authenticated and request.user.role == 'admin':
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, 'authentication/admin_login.html')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Verify user has admin role
            if user.role == 'admin':
                # Log in the user
                django_login(request, user)

                # Populate session for compatibility with existing decorators
                request.session['user'] = {
                    'role': 'admin',
                    'user_id': user.id,
                    'username': user.username,
                    'full_name': user.get_full_name(),
                    'email': user.email,
                    'onboarding_complete': True,
                    'userinfo': {
                        'name': user.get_full_name(),
                        'email': user.email,
                    }
                }

                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')

                # Redirect to admin dashboard
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Access denied. Admin credentials required.')
        else:
            messages.error(request, 'Invalid username or password.')

    context = {
        'page_title': 'Admin Login',
    }
    return render(request, 'authentication/admin_login.html', context)


@require_http_methods(["GET", "POST"])
def admin_logout(request):
    """
    Admin logout view
    Clears Django authentication session
    """
    if request.user.is_authenticated:
        user_name = request.user.get_full_name() or request.user.username
        django_logout(request)
        request.session.flush()
        messages.success(request, f'Goodbye, {user_name}! You have been logged out.')

    return redirect('admin_login')
