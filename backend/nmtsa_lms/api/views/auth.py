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
