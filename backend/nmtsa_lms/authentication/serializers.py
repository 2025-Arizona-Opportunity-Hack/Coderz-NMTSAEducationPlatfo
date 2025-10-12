"""
Serializers for authentication app
Handles user profiles, onboarding, and JWT token responses
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, TeacherProfile, StudentProfile


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    Returns basic user information
    """
    full_name = serializers.SerializerMethodField()
    is_student = serializers.BooleanField(read_only=True)
    is_teacher = serializers.BooleanField(read_only=True)
    is_admin_user = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'auth0_id',
            'profile_picture',
            'onboarding_complete',
            'is_student',
            'is_teacher',
            'is_admin_user',
        ]
        read_only_fields = ['id', 'username', 'auth0_id']

    def get_full_name(self, obj):
        return obj.get_full_name()


class TeacherProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for TeacherProfile model
    Includes nested user data
    """
    user = UserSerializer(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    is_pending = serializers.BooleanField(read_only=True)

    class Meta:
        model = TeacherProfile
        fields = [
            'id',
            'user',
            'bio',
            'credentials',
            'resume',
            'certifications',
            'verification_status',
            'verification_notes',
            'verified_at',
            'specialization',
            'years_experience',
            'is_verified',
            'is_pending',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'verification_status',
            'verification_notes',
            'verified_at',
            'created_at',
            'updated_at',
        ]


class TeacherProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating teacher profile (without nested user)
    Used during onboarding and profile updates
    """

    class Meta:
        model = TeacherProfile
        fields = [
            'bio',
            'credentials',
            'resume',
            'certifications',
            'specialization',
            'years_experience',
        ]

    def validate_years_experience(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Years of experience cannot be negative.")
        if value is not None and value > 100:
            raise serializers.ValidationError("Years of experience seems unrealistic.")
        return value


class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for StudentProfile model
    Includes nested user data
    """
    user = UserSerializer(read_only=True)
    relationship_display = serializers.CharField(source='get_relationship_display', read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            'id',
            'user',
            'relationship',
            'relationship_display',
            'care_recipient_name',
            'care_recipient_age',
            'special_needs',
            'learning_goals',
            'interests',
            'accessibility_needs',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating student profile (without nested user)
    Used during onboarding and profile updates
    """

    class Meta:
        model = StudentProfile
        fields = [
            'relationship',
            'care_recipient_name',
            'care_recipient_age',
            'special_needs',
            'learning_goals',
            'interests',
            'accessibility_needs',
        ]

    def validate_care_recipient_age(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Age cannot be negative.")
        if value is not None and value > 150:
            raise serializers.ValidationError("Age seems unrealistic.")
        return value

    def validate_relationship(self, value):
        valid_choices = [choice[0] for choice in StudentProfile.RELATIONSHIP_CHOICES]
        if value and value not in valid_choices:
            raise serializers.ValidationError(f"Invalid relationship choice. Must be one of: {', '.join(valid_choices)}")
        return value


class RoleSelectionSerializer(serializers.Serializer):
    """
    Serializer for role selection during onboarding
    """
    role = serializers.ChoiceField(choices=['student', 'teacher'])

    def validate_role(self, value):
        if value not in ['student', 'teacher']:
            raise serializers.ValidationError("Role must be either 'student' or 'teacher'.")
        return value


class TeacherOnboardingSerializer(serializers.Serializer):
    """
    Serializer for teacher onboarding form
    Handles profile data and file uploads
    """
    bio = serializers.CharField(required=False, allow_blank=True)
    credentials = serializers.CharField(required=False, allow_blank=True)
    specialization = serializers.CharField(max_length=200, required=False, allow_blank=True)
    years_experience = serializers.IntegerField(required=False, allow_null=True)
    resume = serializers.FileField(required=False, allow_null=True)
    certifications = serializers.FileField(required=False, allow_null=True)

    def validate_years_experience(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Years of experience cannot be negative.")
        if value is not None and value > 100:
            raise serializers.ValidationError("Years of experience seems unrealistic.")
        return value

    def validate_resume(self, value):
        if value:
            # Check file size (max 10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("Resume file size cannot exceed 10MB.")
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx']
            import os
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in allowed_extensions:
                raise serializers.ValidationError(f"Resume must be a PDF or Word document. Allowed: {', '.join(allowed_extensions)}")
        return value

    def validate_certifications(self, value):
        if value:
            # Check file size (max 10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("Certifications file size cannot exceed 10MB.")
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.zip']
            import os
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in allowed_extensions:
                raise serializers.ValidationError(f"Certifications must be a PDF, Word document, or ZIP file. Allowed: {', '.join(allowed_extensions)}")
        return value


class StudentOnboardingSerializer(serializers.Serializer):
    """
    Serializer for student onboarding form
    Handles student profile data
    """
    relationship = serializers.ChoiceField(
        choices=StudentProfile.RELATIONSHIP_CHOICES,
        required=False,
        allow_blank=True
    )
    care_recipient_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    care_recipient_age = serializers.IntegerField(required=False, allow_null=True)
    special_needs = serializers.CharField(required=False, allow_blank=True)
    learning_goals = serializers.CharField(required=False, allow_blank=True)
    interests = serializers.CharField(required=False, allow_blank=True)
    accessibility_needs = serializers.CharField(required=False, allow_blank=True)

    def validate_care_recipient_age(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Age cannot be negative.")
        if value is not None and value > 150:
            raise serializers.ValidationError("Age seems unrealistic.")
        return value


class ProfileUpdateSerializer(serializers.Serializer):
    """
    Serializer for general profile updates
    Handles both user basic info and role-specific profile data
    """
    # User basic info
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)

    # Teacher-specific fields
    bio = serializers.CharField(required=False, allow_blank=True)
    specialization = serializers.CharField(max_length=200, required=False, allow_blank=True)
    years_experience = serializers.IntegerField(required=False, allow_null=True)

    # Student-specific fields
    relationship = serializers.ChoiceField(
        choices=StudentProfile.RELATIONSHIP_CHOICES,
        required=False,
        allow_blank=True
    )
    learning_goals = serializers.CharField(required=False, allow_blank=True)
    interests = serializers.CharField(required=False, allow_blank=True)
    accessibility_needs = serializers.CharField(required=False, allow_blank=True)

    def validate_years_experience(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Years of experience cannot be negative.")
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that includes user data in the response
    Used after Auth0 authentication
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['role'] = user.role
        token['auth0_id'] = user.auth0_id
        token['onboarding_complete'] = user.onboarding_complete

        # Add teacher-specific claims
        if user.role == 'teacher' and hasattr(user, 'teacher_profile'):
            token['verification_status'] = user.teacher_profile.verification_status
            token['is_verified'] = user.teacher_profile.is_verified

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user data to response
        data['user'] = UserSerializer(self.user).data

        # Add role-specific profile data
        if self.user.role == 'teacher' and hasattr(self.user, 'teacher_profile'):
            data['teacher_profile'] = TeacherProfileSerializer(self.user.teacher_profile).data
        elif self.user.role == 'student' and hasattr(self.user, 'student_profile'):
            data['student_profile'] = StudentProfileSerializer(self.user.student_profile).data

        return data


class AdminLoginSerializer(serializers.Serializer):
    """
    Serializer for admin login via username/password
    """
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError("Both username and password are required.")

        return attrs
