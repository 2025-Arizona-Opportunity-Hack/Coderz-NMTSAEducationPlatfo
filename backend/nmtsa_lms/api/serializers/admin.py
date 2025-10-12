"""
Admin Serializers
Handles serialization for admin dashboard, teacher verification, course review, user management
"""
from rest_framework import serializers
from authentication.models import User, TeacherProfile, StudentProfile, Enrollment
from teacher_dash.models import Course, Module
from django.utils import timezone


class AdminDashboardStatsSerializer(serializers.Serializer):
    """Admin dashboard overview statistics"""
    total_users = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    total_admins = serializers.IntegerField()
    
    total_courses = serializers.IntegerField()
    published_courses = serializers.IntegerField()
    draft_courses = serializers.IntegerField()
    pending_review = serializers.IntegerField()
    
    total_enrollments = serializers.IntegerField()
    active_enrollments = serializers.IntegerField()
    
    pending_teacher_verifications = serializers.IntegerField()
    
    recent_signups = serializers.ListField(child=serializers.DictField())
    recent_enrollments = serializers.ListField(child=serializers.DictField())


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for listings"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'date_joined', 'is_active'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class StudentDetailSerializer(serializers.ModelSerializer):
    """Detailed student information"""
    user = UserBasicSerializer()
    total_enrollments = serializers.SerializerMethodField()
    completed_courses = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentProfile
        fields = [
            'user', 'phone_number', 'date_of_birth', 'grade_level',
            'school_name', 'parent_name', 'parent_email', 'parent_phone',
            'total_enrollments', 'completed_courses'
        ]
    
    def get_total_enrollments(self, obj):
        return Enrollment.objects.filter(user=obj.user, is_active=True).count()
    
    def get_completed_courses(self, obj):
        return Enrollment.objects.filter(
            user=obj.user,
            is_active=True,
            progress_percentage=100
        ).count()


class TeacherDetailSerializer(serializers.ModelSerializer):
    """Detailed teacher information"""
    user = UserBasicSerializer()
    total_courses = serializers.SerializerMethodField()
    published_courses = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherProfile
        fields = [
            'user', 'phone_number', 'bio', 'specialization',
            'years_of_experience', 'education_background',
            'certifications', 'website', 'linkedin', 'twitter',
            'verification_status', 'is_verified', 'verified_at',
            'rejection_reason', 'resume', 'certification_documents',
            'total_courses', 'published_courses', 'total_students'
        ]
    
    def get_total_courses(self, obj):
        return Course.objects.filter(published_by=obj.user).count()
    
    def get_published_courses(self, obj):
        return Course.objects.filter(published_by=obj.user, is_published=True).count()
    
    def get_total_students(self, obj):
        courses = Course.objects.filter(published_by=obj.user)
        return Enrollment.objects.filter(course__in=courses, is_active=True).values('user').distinct().count()


class TeacherVerificationSerializer(serializers.ModelSerializer):
    """Teacher verification application details"""
    user = UserBasicSerializer()
    
    class Meta:
        model = TeacherProfile
        fields = [
            'user', 'phone_number', 'bio', 'specialization',
            'years_of_experience', 'education_background',
            'certifications', 'resume', 'certification_documents',
            'verification_status', 'is_verified', 'verified_at', 'rejection_reason'
        ]


class TeacherVerificationActionSerializer(serializers.Serializer):
    """Approve or reject teacher verification"""
    action = serializers.ChoiceField(choices=['approve', 'reject'], required=True)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        if data.get('action') == 'reject' and not data.get('rejection_reason'):
            raise serializers.ValidationError({
                'rejection_reason': 'Rejection reason is required when rejecting'
            })
        return data


class CourseReviewSerializer(serializers.ModelSerializer):
    """Course pending review details"""
    teacher = serializers.SerializerMethodField()
    modules_count = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'teacher', 'category',
            'thumbnail', 'is_paid', 'price', 'is_published',
            'is_submitted_for_review', 'published_date',
            'modules_count', 'lessons_count'
        ]
    
    def get_teacher(self, obj):
        return {
            'id': obj.published_by.id,
            'name': obj.published_by.get_full_name() or obj.published_by.username,
            'email': obj.published_by.email
        }
    
    def get_modules_count(self, obj):
        return obj.modules.count()
    
    def get_lessons_count(self, obj):
        total = 0
        for module in obj.modules.all():
            total += module.lessons.count()
        return total


class CourseReviewActionSerializer(serializers.Serializer):
    """Approve or reject course for publication"""
    action = serializers.ChoiceField(choices=['approve', 'reject'], required=True)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        if data.get('action') == 'reject' and not data.get('rejection_reason'):
            raise serializers.ValidationError({
                'rejection_reason': 'Rejection reason is required when rejecting'
            })
        return data


class UserManagementSerializer(serializers.ModelSerializer):
    """User management with role updates"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['username', 'date_joined', 'last_login']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserUpdateSerializer(serializers.ModelSerializer):
    """Update user information"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'is_active']
    
    def validate_role(self, value):
        if value not in ['student', 'teacher', 'admin']:
            raise serializers.ValidationError("Invalid role")
        return value


class EnrollmentManagementSerializer(serializers.ModelSerializer):
    """Enrollment management for admins"""
    student = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'course', 'enrolled_at',
            'progress_percentage', 'is_active'
        ]
    
    def get_student(self, obj):
        return {
            'id': obj.user.id,
            'name': obj.user.get_full_name() or obj.user.username,
            'email': obj.user.email
        }
    
    def get_course(self, obj):
        return {
            'id': obj.course.id,
            'title': obj.course.title,
            'teacher': obj.course.published_by.get_full_name() or obj.course.published_by.username
        }


class CourseManagementSerializer(serializers.ModelSerializer):
    """Course management for admins"""
    teacher = serializers.SerializerMethodField()
    enrollment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'teacher', 'category',
            'thumbnail', 'is_paid', 'price', 'is_published',
            'is_submitted_for_review', 'published_date', 'enrollment_count'
        ]
    
    def get_teacher(self, obj):
        return {
            'id': obj.published_by.id,
            'name': obj.published_by.get_full_name() or obj.published_by.username,
            'email': obj.published_by.email
        }
    
    def get_enrollment_count(self, obj):
        return Enrollment.objects.filter(course=obj, is_active=True).count()


class CourseStatusUpdateSerializer(serializers.Serializer):
    """Update course publication status"""
    is_published = serializers.BooleanField(required=False)
    is_submitted_for_review = serializers.BooleanField(required=False)
