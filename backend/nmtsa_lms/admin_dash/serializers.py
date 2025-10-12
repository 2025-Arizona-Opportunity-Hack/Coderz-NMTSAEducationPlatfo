"""
Serializers for admin dashboard
Handles teacher verification, course review, and admin statistics
"""

from rest_framework import serializers
from authentication.models import User, TeacherProfile
from teacher_dash.models import Course, Module, Lesson


class AdminDashboardStatsSerializer(serializers.Serializer):
    """
    Serializer for admin dashboard statistics
    """
    pending_teachers = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    total_students = serializers.IntegerField()
    pending_courses = serializers.IntegerField()


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Basic user information for admin views
    """
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role']

    def get_full_name(self, obj):
        return obj.get_full_name()


class TeacherVerificationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for pending teacher verification list
    """
    user = UserBasicSerializer(read_only=True)

    class Meta:
        model = TeacherProfile
        fields = [
            'id',
            'user',
            'specialization',
            'years_experience',
            'verification_status',
            'created_at',
        ]


class TeacherVerificationDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for teacher verification review
    Includes all profile information for admin to review
    """
    user = UserBasicSerializer(read_only=True)
    resume_url = serializers.SerializerMethodField()
    certifications_url = serializers.SerializerMethodField()

    class Meta:
        model = TeacherProfile
        fields = [
            'id',
            'user',
            'bio',
            'credentials',
            'resume',
            'resume_url',
            'certifications',
            'certifications_url',
            'verification_status',
            'verification_notes',
            'verified_at',
            'verified_by',
            'specialization',
            'years_experience',
            'created_at',
            'updated_at',
        ]

    def get_resume_url(self, obj):
        if obj.resume:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.resume.url)
            return obj.resume.url
        return None

    def get_certifications_url(self, obj):
        if obj.certifications:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.certifications.url)
            return obj.certifications.url
        return None


class TeacherVerificationActionSerializer(serializers.Serializer):
    """
    Serializer for teacher verification action (approve/reject)
    """
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_action(self, value):
        if value not in ['approve', 'reject']:
            raise serializers.ValidationError("Action must be 'approve' or 'reject'")
        return value


class CourseReviewListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for courses pending review
    """
    published_by = UserBasicSerializer(read_only=True)
    module_count = serializers.SerializerMethodField()
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'published_by',
            'published_date',
            'is_submitted_for_review',
            'admin_approved',
            'module_count',
            'lesson_count',
        ]

    def get_module_count(self, obj):
        return obj.modules.count()

    def get_lesson_count(self, obj):
        total = 0
        for module in obj.modules.all():
            total += module.lessons.count()
        return total


class LessonBasicSerializer(serializers.ModelSerializer):
    """
    Basic lesson information for course review
    """
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'lesson_type', 'duration']


class ModuleWithLessonsSerializer(serializers.ModelSerializer):
    """
    Module serializer with nested lessons for course review
    """
    lessons = LessonBasicSerializer(many=True, read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'lessons', 'lesson_count']

    def get_lesson_count(self, obj):
        return obj.lessons.count()


class CourseReviewDetailSerializer(serializers.ModelSerializer):
    """
    Detailed course serializer for admin review
    Includes all modules and lessons
    """
    published_by = UserBasicSerializer(read_only=True)
    modules = ModuleWithLessonsSerializer(many=True, read_only=True)
    module_count = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'published_by',
            'published_date',
            'is_published',
            'is_submitted_for_review',
            'admin_approved',
            'admin_review_feedback',
            'price',
            'is_paid',
            'num_enrollments',
            'modules',
            'module_count',
            'total_lessons',
        ]

    def get_module_count(self, obj):
        return obj.modules.count()

    def get_total_lessons(self, obj):
        total = 0
        for module in obj.modules.all():
            total += module.lessons.count()
        return total


class CourseReviewActionSerializer(serializers.Serializer):
    """
    Serializer for course review action (approve/reject)
    """
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    feedback = serializers.CharField(required=False, allow_blank=True)

    def validate_action(self, value):
        if value not in ['approve', 'reject']:
            raise serializers.ValidationError("Action must be 'approve' or 'reject'")
        return value
