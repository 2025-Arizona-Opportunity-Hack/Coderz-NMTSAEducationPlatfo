"""
Authentication API Views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone

from authentication.models import User
from api.serializers import UserSerializer


class AdminLoginView(APIView):
    """
    Admin login endpoint - username/password authentication
    Returns JWT tokens for API access
    
    POST /api/auth/admin/login
    {
        "username": "admin",
        "password": "password"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'message': 'Please provide both username and password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response(
                {'message': 'Invalid username or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verify user has admin role
        if user.role != 'admin':
            return Response(
                {'message': 'Access denied. Admin credentials required.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Serialize user data
        user_serializer = UserSerializer(user)
        
        return Response({
            'token': str(refresh.access_token),
            'refreshToken': str(refresh),
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    """
    Get current authenticated user profile
    
    GET /api/auth/me
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class LogoutView(APIView):
    """
    Logout endpoint (for JWT, mainly client-side token removal)
    
    POST /api/auth/logout
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # For JWT, we could blacklist the token here if needed
            # For now, client-side token removal is sufficient
            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class OAuthSignInView(APIView):
    """
    OAuth sign-in endpoint - receives user data from frontend OAuth and creates/updates user
    Frontend handles OAuth, backend just manages user account and returns JWT
    
    POST /api/auth/oauth/signin
    {
        "provider": "google|microsoft",
        "email": "user@example.com",
        "name": "John Doe",
        "picture": "https://..." # Optional
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        provider = request.data.get('provider')
        email = request.data.get('email')
        name = request.data.get('name')
        picture = request.data.get('picture')
        
        if not provider or not email or not name:
            return Response(
                {'message': 'Provider, email, and name are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'first_name': name.split()[0] if name and ' ' in name else name or '',
                    'last_name': ' '.join(name.split()[1:]) if name and ' ' in name else '',
                    'role': 'student',  # Default role for OAuth users
                    'is_active': True,
                }
            )
            
            # Update profile picture if provided
            if picture and not user.profile_picture:
                user.profile_picture = picture
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login', 'profile_picture'] if picture else ['last_login'])
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Serialize user data
            user_serializer = UserSerializer(user)
            
            return Response({
                'token': str(refresh.access_token),
                'refreshToken': str(refresh),
                'user': user_serializer.data,
                'isNewUser': created
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'message': f'OAuth sign-in failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
