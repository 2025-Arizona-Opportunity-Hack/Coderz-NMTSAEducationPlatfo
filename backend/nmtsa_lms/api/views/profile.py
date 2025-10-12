"""
Profile and Onboarding API Views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from authentication.models import User, TeacherProfile, StudentProfile
from api.serializers import (
    RoleSelectionSerializer,
    TeacherOnboardingSerializer,
    StudentOnboardingSerializer,
    UserProfileSerializer,
)


class SelectRoleView(APIView):
    """
    Select user role during onboarding
    
    POST /api/onboarding/select-role
    {
        "role": "student" | "teacher"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = RoleSelectionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'message': 'Invalid role selection', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        role = serializer.validated_data['role']
        user = request.user
        
        # Update user role
        user.role = role
        user.save(update_fields=['role'])
        
        # Create profile if it doesn't exist
        if role == 'teacher':
            TeacherProfile.objects.get_or_create(user=user)
        else:
            StudentProfile.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Role selected successfully',
            'role': role
        }, status=status.HTTP_200_OK)


class TeacherOnboardingView(APIView):
    """
    Complete teacher onboarding
    
    POST /api/onboarding/teacher
    Content-Type: multipart/form-data
    {
        "bio": "...",
        "credentials": "...",
        "specialization": "...",
        "years_experience": 5,
        "resume": <file>,
        "certifications": <file>
    }
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request):
        user = request.user
        
        if user.role != 'teacher':
            return Response(
                {'message': 'User must be a teacher to complete teacher onboarding'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = TeacherOnboardingSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'message': 'Invalid onboarding data', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create teacher profile
        teacher_profile, created = TeacherProfile.objects.get_or_create(user=user)
        
        # Update profile fields
        data = serializer.validated_data
        teacher_profile.bio = data.get('bio', teacher_profile.bio)
        teacher_profile.credentials = data.get('credentials', teacher_profile.credentials)
        teacher_profile.specialization = data.get('specialization', teacher_profile.specialization)
        teacher_profile.years_experience = data.get('years_experience', teacher_profile.years_experience)
        
        # Handle file uploads
        if 'resume' in request.FILES:
            teacher_profile.resume = request.FILES['resume']
        if 'certifications' in request.FILES:
            teacher_profile.certifications = request.FILES['certifications']
        
        teacher_profile.save()
        
        # Mark onboarding as complete
        user.onboarding_complete = True
        user.save(update_fields=['onboarding_complete'])
        
        # Return updated user profile
        profile_serializer = UserProfileSerializer(user, context={'request': request})
        
        return Response({
            'message': 'Teacher onboarding completed successfully',
            'user': profile_serializer.data
        }, status=status.HTTP_200_OK)


class StudentOnboardingView(APIView):
    """
    Complete student onboarding
    
    POST /api/onboarding/student
    {
        "relationship": "parent",
        "care_recipient_name": "...",
        "care_recipient_age": 5,
        "special_needs": "...",
        "learning_goals": "...",
        "interests": "...",
        "accessibility_needs": "..."
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        if user.role != 'student':
            return Response(
                {'message': 'User must be a student to complete student onboarding'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = StudentOnboardingSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'message': 'Invalid onboarding data', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create student profile
        student_profile, created = StudentProfile.objects.get_or_create(user=user)
        
        # Update profile fields
        data = serializer.validated_data
        student_profile.relationship = data.get('relationship', student_profile.relationship)
        student_profile.care_recipient_name = data.get('care_recipient_name', student_profile.care_recipient_name)
        student_profile.care_recipient_age = data.get('care_recipient_age', student_profile.care_recipient_age)
        student_profile.special_needs = data.get('special_needs', student_profile.special_needs)
        student_profile.learning_goals = data.get('learning_goals', student_profile.learning_goals)
        student_profile.interests = data.get('interests', student_profile.interests)
        student_profile.accessibility_needs = data.get('accessibility_needs', student_profile.accessibility_needs)
        
        student_profile.save()
        
        # Mark onboarding as complete
        user.onboarding_complete = True
        user.save(update_fields=['onboarding_complete'])
        
        # Return updated user profile
        profile_serializer = UserProfileSerializer(user, context={'request': request})
        
        return Response({
            'message': 'Student onboarding completed successfully',
            'user': profile_serializer.data
        }, status=status.HTTP_200_OK)


class ProfileView(APIView):
    """
    Get or update user profile
    
    GET /api/profile
    Returns complete user profile with role-specific data
    
    PUT /api/profile
    Update basic user information
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        user = request.user
        
        # Update basic user fields
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.save(update_fields=['first_name', 'last_name'])
        
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response({
            'message': 'Profile updated successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
