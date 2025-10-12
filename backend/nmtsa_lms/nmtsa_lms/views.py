import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import quote_plus, urlencode


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
    return render(
        request,
        "landing.html",
        context={
            "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4),
        },
    )

def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

def callback(request):
    """
    Auth0 OAuth callback handler
    Creates or updates user in database and redirects to frontend
    """
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token

    # Extract user info from token
    userinfo = token.get('userinfo', {})
    auth0_id = userinfo.get('sub')
    email = userinfo.get('email')
    name = userinfo.get('name')

    if auth0_id:
        # Import here to avoid circular dependency
        from authentication.models import User

        try:
            # Check if user exists in our database
            user = User.objects.get(auth0_id=auth0_id)
            # Update session with user ID for backend authentication
            request.session['user_id'] = str(user.id)
            
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create(
                auth0_id=auth0_id,
                email=email,
                username=email.split('@')[0] if email else auth0_id,
                first_name=name.split()[0] if name else '',
                last_name=' '.join(name.split()[1:]) if name and len(name.split()) > 1 else '',
            )
            request.session['user_id'] = str(user.id)

    # Redirect to frontend dashboard
    # Frontend will check session and handle onboarding if needed
    frontend_url = "http://localhost:5173/dashboard"
    return redirect(frontend_url)


def logout(request):
    request.session.clear()

    # Redirect to Auth0 logout, then back to frontend home page
    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": "http://localhost:5173",  # Frontend URL
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )