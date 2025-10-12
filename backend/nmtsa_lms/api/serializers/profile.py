"""
Profile and Onboarding Serializers
"""
from rest_framework import serializers
from authentication.models import User, TeacherProfile, StudentProfile


class TeacherProfileSerializer(serializers.ModelSerializer):
    """Serializer for teacher profile"""
    resume_url = serializers.SerializerMethodField()
    certifications_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherProfile
        fields = [
            'bio',
            'credentials',
            'specialization',
            'years_experience',
            'verification_status',
            'resume',
            'resume_url',
            'certifications',
            'certifications_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['verification_status', 'created_at', 'updated_at']
    
    def get_resume_url(self, obj):
        if obj.resume:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.resume.url)
        return None
    
    def get_certifications_url(self, obj):
        if obj.certifications:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.certifications.url)
        return None


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for student profile"""
    
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
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for complete user profile with role-specific data"""
    teacher_profile = TeacherProfileSerializer(read_only=True)
    student_profile = StudentProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'profile_picture',
            'onboarding_complete',
            'is_active',
            'date_joined',
            'teacher_profile',
            'student_profile',
        ]
        read_only_fields = ['id', 'username', 'email', 'date_joined']


class RoleSelectionSerializer(serializers.Serializer):
    """Serializer for role selection during onboarding"""
    role = serializers.ChoiceField(choices=['student', 'teacher'])


class TeacherOnboardingSerializer(serializers.Serializer):
    """Serializer for teacher onboarding data"""
    bio = serializers.CharField(max_length=5000, allow_blank=True, required=False)
    credentials = serializers.CharField(max_length=5000, allow_blank=True, required=False)
    specialization = serializers.CharField(max_length=200, allow_blank=True, required=False)
    years_experience = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    resume = serializers.FileField(required=False, allow_null=True)
    certifications = serializers.FileField(required=False, allow_null=True)


class StudentOnboardingSerializer(serializers.Serializer):
    """Serializer for student onboarding data"""
    relationship = serializers.ChoiceField(
        choices=StudentProfile.RELATIONSHIP_CHOICES,
        allow_blank=True,
        required=False
    )
    care_recipient_name = serializers.CharField(
        max_length=200,
        allow_blank=True,
        required=False
    )
    care_recipient_age = serializers.IntegerField(
        min_value=0,
        required=False,
        allow_null=True
    )
    special_needs = serializers.CharField(
        max_length=5000,
        allow_blank=True,
        required=False
    )
    learning_goals = serializers.CharField(
        max_length=5000,
        allow_blank=True,
        required=False
    )
    interests = serializers.CharField(
        max_length=5000,
        allow_blank=True,
        required=False
    )
    accessibility_needs = serializers.CharField(
        max_length=5000,
        allow_blank=True,
        required=False
    )
