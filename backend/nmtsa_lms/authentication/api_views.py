"""
API views for authentication app
Handles user authentication, onboarding, and profile management
"""

from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError

from .models import User, TeacherProfile, StudentProfile
from .serializers import (
    UserSerializer,
    TeacherProfileSerializer,
    StudentProfileSerializer,
    TeacherProfileUpdateSerializer,
    StudentProfileUpdateSerializer,
    RoleSelectionSerializer,
    TeacherOnboardingSerializer,
    StudentOnboardingSerializer,
    ProfileUpdateSerializer,
    AdminLoginSerializer,
)
from .permissions import IsStudent, IsTeacher, IsAdmin


class CurrentUserView(APIView):
    """
    GET /api/v1/auth/me/
    Returns the current authenticated user's profile data
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        data = serializer.data

        # Add role-specific profile data
        if user.role == 'teacher' and hasattr(user, 'teacher_profile'):
            data['teacher_profile'] = TeacherProfileSerializer(user.teacher_profile).data
        elif user.role == 'student' and hasattr(user, 'student_profile'):
            data['student_profile'] = StudentProfileSerializer(user.student_profile).data

        return Response(data)


class SelectRoleView(APIView):
    """
    POST /api/v1/auth/select-role/
    Allows user to select their role (student or teacher) during onboarding
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RoleSelectionSerializer(data=request.data)
        if serializer.is_valid():
            role = serializer.validated_data['role']

            # Update user role
            user = request.user
            user.role = role
            user.save()

            # Return updated user data
            return Response(
                {
                    'message': f'Role set to {role}',
                    'user': UserSerializer(user).data
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherOnboardingView(APIView):
    """
    GET /api/v1/auth/onboarding/teacher/
    POST /api/v1/auth/onboarding/teacher/

    GET: Returns current teacher profile data
    POST: Updates teacher profile during onboarding
    """
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):
        user = request.user
        teacher_profile, created = TeacherProfile.objects.get_or_create(user=user)
        serializer = TeacherProfileSerializer(teacher_profile)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        teacher_profile, created = TeacherProfile.objects.get_or_create(user=user)

        serializer = TeacherOnboardingSerializer(data=request.data)
        if serializer.is_valid():
            # Update teacher profile fields
            for field, value in serializer.validated_data.items():
                setattr(teacher_profile, field, value)

            teacher_profile.save()

            # Mark onboarding as complete
            user.onboarding_complete = True
            user.save()

            return Response(
                {
                    'message': 'Teacher profile updated successfully. Your application is pending admin verification.',
                    'teacher_profile': TeacherProfileSerializer(teacher_profile).data,
                    'user': UserSerializer(user).data
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentOnboardingView(APIView):
    """
    GET /api/v1/auth/onboarding/student/
    POST /api/v1/auth/onboarding/student/

    GET: Returns current student profile data
    POST: Updates student profile during onboarding
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        user = request.user
        student_profile, created = StudentProfile.objects.get_or_create(user=user)
        serializer = StudentProfileSerializer(student_profile)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        student_profile, created = StudentProfile.objects.get_or_create(user=user)

        serializer = StudentOnboardingSerializer(data=request.data)
        if serializer.is_valid():
            # Update student profile fields
            for field, value in serializer.validated_data.items():
                setattr(student_profile, field, value)

            student_profile.save()

            # Mark onboarding as complete
            user.onboarding_complete = True
            user.save()

            return Response(
                {
                    'message': 'Student profile completed successfully. Welcome to NMTSA Learning!',
                    'student_profile': StudentProfileSerializer(student_profile).data,
                    'user': UserSerializer(user).data
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileSettingsView(APIView):
    """
    GET /api/v1/auth/profile/
    PUT /api/v1/auth/profile/

    GET: Returns user profile data based on role
    PUT: Updates user profile (both basic info and role-specific fields)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = UserSerializer(user).data

        # Add role-specific profile
        if user.role == 'teacher' and hasattr(user, 'teacher_profile'):
            data['teacher_profile'] = TeacherProfileSerializer(user.teacher_profile).data
        elif user.role == 'student' and hasattr(user, 'student_profile'):
            data['student_profile'] = StudentProfileSerializer(user.student_profile).data

        return Response(data)

    def put(self, request):
        user = request.user
        serializer = ProfileUpdateSerializer(data=request.data)

        if serializer.is_valid():
            # Update user basic fields
            if 'first_name' in serializer.validated_data:
                user.first_name = serializer.validated_data['first_name']
            if 'last_name' in serializer.validated_data:
                user.last_name = serializer.validated_data['last_name']
            user.save()

            # Update teacher profile
            if user.role == 'teacher' and hasattr(user, 'teacher_profile'):
                profile = user.teacher_profile
                if 'bio' in serializer.validated_data:
                    profile.bio = serializer.validated_data['bio']
                if 'specialization' in serializer.validated_data:
                    profile.specialization = serializer.validated_data['specialization']
                if 'years_experience' in serializer.validated_data:
                    profile.years_experience = serializer.validated_data['years_experience']
                profile.save()

            # Update student profile
            elif user.role == 'student' and hasattr(user, 'student_profile'):
                profile = user.student_profile
                if 'relationship' in serializer.validated_data:
                    profile.relationship = serializer.validated_data['relationship']
                if 'learning_goals' in serializer.validated_data:
                    profile.learning_goals = serializer.validated_data['learning_goals']
                if 'interests' in serializer.validated_data:
                    profile.interests = serializer.validated_data['interests']
                if 'accessibility_needs' in serializer.validated_data:
                    profile.accessibility_needs = serializer.validated_data['accessibility_needs']
                profile.save()

            return Response(
                {
                    'message': 'Profile updated successfully',
                    'user': UserSerializer(user).data
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    Blacklists the refresh token to log out the user
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AdminLoginView(APIView):
    """
    POST /api/v1/auth/admin/login/
    Admin login using Django username/password authentication
    Returns JWT tokens for admin users
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Authenticate user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Verify user has admin role
                if user.role == 'admin':
                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)

                    # Add custom claims
                    refresh['email'] = user.email
                    refresh['role'] = user.role
                    refresh['onboarding_complete'] = True

                    return Response(
                        {
                            'access': str(refresh.access_token),
                            'refresh': str(refresh),
                            'user': UserSerializer(user).data,
                            'message': f'Welcome back, {user.get_full_name() or user.username}!'
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {'error': 'Access denied. Admin credentials required.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                return Response(
                    {'error': 'Invalid username or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminLogoutView(APIView):
    """
    POST /api/v1/auth/admin/logout/
    Logout admin user by blacklisting refresh token
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {'message': 'Admin logged out successfully'},
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
