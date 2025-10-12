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
    Creates or updates user in database and returns JWT tokens
    Modified to return JSON with JWT tokens instead of redirecting
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    from authentication.serializers import UserSerializer, TeacherProfileSerializer, StudentProfileSerializer
    from django.http import JsonResponse

    try:
        token = oauth.auth0.authorize_access_token(request)
        request.session["user"] = token

        # Extract user info from token
        userinfo = token.get('userinfo', {})
        auth0_id = userinfo.get('sub')
        email = userinfo.get('email')
        name = userinfo.get('name', '')
        picture = userinfo.get('picture')

        if not auth0_id:
            return JsonResponse(
                {'error': 'Auth0 ID not found in token'},
                status=400
            )

        # Import here to avoid circular dependency
        from authentication.models import User

        # Parse name into first and last name
        name_parts = name.split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Get or create user
        try:
            user = User.objects.get(auth0_id=auth0_id)

            # Update user info from Auth0 if changed
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.profile_picture = picture
            user.save()

        except User.DoesNotExist:
            # Create new user
            username = email.split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                auth0_id=auth0_id,
                profile_picture=picture,
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Add custom claims to token
        refresh['email'] = user.email
        refresh['role'] = user.role
        refresh['auth0_id'] = user.auth0_id
        refresh['onboarding_complete'] = user.onboarding_complete

        # Add teacher-specific claims
        if user.role == 'teacher' and hasattr(user, 'teacher_profile'):
            refresh['verification_status'] = user.teacher_profile.verification_status
            refresh['is_verified'] = user.teacher_profile.is_verified

        # Prepare response data
        response_data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }

        # Add role-specific profile data
        if user.role == 'teacher' and hasattr(user, 'teacher_profile'):
            response_data['teacher_profile'] = TeacherProfileSerializer(user.teacher_profile).data
        elif user.role == 'student' and hasattr(user, 'student_profile'):
            response_data['student_profile'] = StudentProfileSerializer(user.student_profile).data

        return JsonResponse(response_data, status=200)

    except Exception as e:
        return JsonResponse(
            {
                'error': 'Authentication failed',
                'message': str(e)
            },
            status=400
        )


def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )