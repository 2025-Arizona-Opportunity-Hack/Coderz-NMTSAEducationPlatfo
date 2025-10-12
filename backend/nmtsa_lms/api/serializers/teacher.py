"""
Teacher Management Serializers
Handles teacher dashboard, course/module/lesson management, and analytics
"""
from rest_framework import serializers
from teacher_dash.models import Course, Module, Lesson, VideoLesson, BlogLesson
from authentication.models import Enrollment, TeacherProfile
from lms.models import CompletedLesson
from django.db.models import Count, Avg, Q
from datetime import timedelta
from django.utils import timezone


class TeacherDashboardStatsSerializer(serializers.Serializer):
    """Teacher dashboard statistics"""
    total_courses = serializers.IntegerField()
    published_courses = serializers.IntegerField()
    draft_courses = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    verification_status = serializers.CharField()
    is_verified = serializers.BooleanField()
    recent_enrollments = serializers.ListField()


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course info for teacher lists"""
    enrollment_count = serializers.IntegerField(source='num_enrollments')
    status = serializers.SerializerMethodField()
    thumbnail_url = serializers.URLField(source='thumbnail_url', allow_null=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'thumbnail_url',
            'is_published', 'is_submitted_for_review', 'status',
            'enrollment_count', 'rating', 'price', 'is_paid',
            'published_date', 'difficulty', 'credits'
        ]
    
    def get_status(self, obj):
        if obj.is_published:
            return 'published'
        elif obj.is_submitted_for_review:
            return 'under_review'
        else:
            return 'draft'


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/Update course"""
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Course
        fields = [
            'title', 'description', 'long_description',
            'thumbnail_url', 'category', 'difficulty',
            'price', 'is_paid', 'credits', 'tags',
            'prerequisites', 'learning_objectives'
        ]
    
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        course = Course.objects.create(**validated_data)
        
        # Add tags
        if tags:
            course.tags.add(*tags)
        
        return course
    
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        
        # Update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update tags if provided
        if tags is not None:
            instance.tags.clear()
            if tags:
                instance.tags.add(*tags)
        
        return instance


class ModuleListSerializer(serializers.ModelSerializer):
    """Module list for course detail"""
    lesson_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'order', 'lesson_count']
    
    def get_lesson_count(self, obj):
        return obj.lessons.count()


class ModuleCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/Update module"""
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Module
        fields = ['title', 'description', 'order', 'tags']
    
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        module = Module.objects.create(**validated_data)
        
        if tags:
            module.tags.add(*tags)
        
        return module
    
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if tags is not None:
            instance.tags.clear()
            if tags:
                instance.tags.add(*tags)
        
        return instance


class LessonListSerializer(serializers.ModelSerializer):
    """Lesson list for module"""
    type = serializers.CharField(source='lesson_type')
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'lesson_type', 'type', 'duration', 'order']


class LessonCreateSerializer(serializers.Serializer):
    """Create lesson with video or blog content"""
    title = serializers.CharField(max_length=200)
    lesson_type = serializers.ChoiceField(choices=['video', 'blog'])
    duration = serializers.IntegerField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)
    order = serializers.IntegerField(default=0)
    
    # Video lesson fields
    video_file = serializers.FileField(required=False, allow_null=True)
    transcript = serializers.CharField(required=False, allow_blank=True)
    
    # Blog lesson fields
    content = serializers.CharField(required=False, allow_blank=True)
    images = serializers.ImageField(required=False, allow_null=True)
    
    def validate(self, data):
        """Validate that required fields for lesson type are provided"""
        lesson_type = data.get('lesson_type')
        
        if lesson_type == 'video' and not data.get('video_file'):
            raise serializers.ValidationError({
                'video_file': 'Video file is required for video lessons'
            })
        
        if lesson_type == 'blog' and not data.get('content'):
            raise serializers.ValidationError({
                'content': 'Content is required for blog lessons'
            })
        
        return data


class LessonUpdateSerializer(serializers.Serializer):
    """Update lesson"""
    title = serializers.CharField(max_length=200, required=False)
    duration = serializers.IntegerField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)
    order = serializers.IntegerField(required=False)
    
    # Video lesson fields
    video_file = serializers.FileField(required=False, allow_null=True)
    transcript = serializers.CharField(required=False, allow_blank=True)
    
    # Blog lesson fields
    content = serializers.CharField(required=False, allow_blank=True)
    images = serializers.ImageField(required=False, allow_null=True)


class CourseAnalyticsSerializer(serializers.Serializer):
    """Course analytics data"""
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    total_enrollments = serializers.IntegerField()
    active_enrollments = serializers.IntegerField()
    completed_enrollments = serializers.IntegerField()
    average_progress = serializers.FloatField()
    average_rating = serializers.FloatField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    completion_rate = serializers.FloatField()
    enrollment_by_week = serializers.ListField()
    student_engagement = serializers.DictField()


class TeacherVerificationSerializer(serializers.Serializer):
    """Teacher verification status"""
    verification_status = serializers.CharField()
    submitted_at = serializers.DateTimeField()
    verified_at = serializers.DateTimeField(allow_null=True)
    feedback = serializers.CharField(allow_null=True)
    can_create_courses = serializers.BooleanField()
    can_publish_courses = serializers.BooleanField()
    documents_submitted = serializers.DictField()


class CourseDetailSerializer(SimpleCourseSerializer):
    """Detailed course info for teacher with modules"""
    modules = ModuleListSerializer(many=True, read_only=True)
    total_lessons = serializers.SerializerMethodField()
    total_duration = serializers.SerializerMethodField()
    
    class Meta(SimpleCourseSerializer.Meta):
        fields = SimpleCourseSerializer.Meta.fields + [
            'modules', 'total_lessons', 'total_duration',
            'admin_review_feedback', 'long_description',
            'prerequisites', 'learning_objectives'
        ]
    
    def get_total_lessons(self, obj):
        total = 0
        for module in obj.modules.all():
            total += module.lessons.count()
        return total
    
    def get_total_duration(self, obj):
        total = 0
        for module in obj.modules.all():
            for lesson in module.lessons.all():
                if lesson.duration:
                    total += lesson.duration
        return total


class ModuleDetailSerializer(ModuleListSerializer):
    """Detailed module info with lessons"""
    lessons = LessonListSerializer(many=True, read_only=True)
    
    class Meta(ModuleListSerializer.Meta):
        fields = ModuleListSerializer.Meta.fields + ['lessons']
