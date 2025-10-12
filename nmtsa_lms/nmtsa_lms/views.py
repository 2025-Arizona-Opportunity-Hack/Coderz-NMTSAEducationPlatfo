import json
import os
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from django.templatetags.static import static


oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)


def index(request):
    # Build hero image list from the repo-root heroimages directory (served via STATICFILES_DIRS)
    hero_images_dir = os.path.join(settings.BASE_DIR, 'heroimages')
    hero_images = []
    try:
        if os.path.isdir(hero_images_dir):
            for name in sorted(os.listdir(hero_images_dir)):
                lower = name.lower()
                if lower.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")):
                    hero_images.append(static(f"heroimages/{name}"))
    except Exception:
        # Fail silently; background collage is optional
        hero_images = []

    return render(
        request,
        "landing.html",
        context={
            "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4),
            "hero_images": hero_images,
        },
    )

def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, "legal/privacy.html")

def terms_of_service(request):
    """Terms of Service page"""
    return render(request, "legal/terms.html")

def cookie_policy(request):
    """Cookie Policy page"""
    return render(request, "legal/cookies.html")

def faq(request):
    """FAQ page"""
    return render(request, "faq.html")

def contact(request):
    """Contact page"""
    return render(request, "contact.html")

def login(request):
    # Store the next URL in session if provided
    next_url = request.GET.get('next', '')
    if next_url:
        request.session['next_url'] = next_url
    
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

def callback(request):
    """
    Auth0 OAuth callback handler
    Creates or updates user in database and redirects based on onboarding status
    """
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token

    # Extract user info from token
    userinfo = token.get('userinfo', {})
    auth0_id = userinfo.get('sub')
    
    # Get the stored next URL if available
    next_url = request.session.pop('next_url', None)

    if auth0_id:
        # Import here to avoid circular dependency
        from authentication.models import User

        try:
            # Check if user exists in our database
            user = User.objects.get(auth0_id=auth0_id)

            # User exists - check onboarding status
            if not user.role:
                # No role selected yet - redirect to role selection
                # Store next_url for after onboarding
                if next_url:
                    request.session['next_url'] = next_url
                return redirect(reverse("select_role"))
            elif not user.onboarding_complete:
                # Role selected but onboarding not complete
                # Store next_url for after onboarding
                if next_url:
                    request.session['next_url'] = next_url
                if user.role == 'teacher':
                    return redirect(reverse("teacher_onboarding"))
                elif user.role == 'student':
                    return redirect(reverse("student_onboarding"))
            else:
                # Onboarding complete
                # If there's a next URL and user has completed onboarding, redirect there
                if next_url:
                    return redirect(next_url)
                
                # Otherwise redirect to role-based dashboard
                if user.role == 'teacher':
                    return redirect(reverse("teacher_dashboard"))
                elif user.role == 'student':
                    return redirect(reverse("student_dashboard"))
                elif user.role == 'admin':
                    return redirect(reverse("admin_dashboard"))

        except User.DoesNotExist:
            # New user - redirect to role selection
            # Store next_url for after onboarding
            if next_url:
                request.session['next_url'] = next_url
            return redirect(reverse("select_role"))

    # Fallback to index
    return redirect(request.build_absolute_uri(reverse("landing")))


def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("landing")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )