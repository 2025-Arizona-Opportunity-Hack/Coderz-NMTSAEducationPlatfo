"""
Serializers for student dashboard
Handles courses, learning, discussions, and certificates
"""

from rest_framework import serializers
from authentication.models import User, Enrollment
from teacher_dash.models import Course, Module, Lesson, VideoLesson, BlogLesson, DiscussionPost
from lms.models import CompletedLesson, VideoProgress


# ===== Dashboard & Course Catalog Serializers =====

class TeacherBasicSerializer(serializers.ModelSerializer):
    """Basic teacher information for course displays"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'profile_picture']

    def get_full_name(self, obj):
        return obj.get_full_name()


class CourseListSerializer(serializers.ModelSerializer):
    """Lightweight course serializer for catalog and listings"""
    published_by = TeacherBasicSerializer(read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'published_by',
            'published_date',
            'price',
            'is_paid',
            'num_enrollments',
            'tags',
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    """Enrollment with progress information"""
    course = CourseListSerializer(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id',
            'course',
            'enrolled_at',
            'completed_at',
            'progress_percentage',
            'is_active',
            'is_completed',
        ]


class DashboardStatsSerializer(serializers.Serializer):
    """Dashboard statistics"""
    enrolled_count = serializers.IntegerField()
    completed_count = serializers.IntegerField()
    learning_hours = serializers.IntegerField()
    in_progress_courses = EnrollmentSerializer(many=True)
    recommended_courses = CourseListSerializer(many=True)


# ===== Course Detail Serializers =====

class LessonListSerializer(serializers.ModelSerializer):
    """Lesson information for course detail view"""
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'lesson_type', 'duration']


class ModuleListSerializer(serializers.ModelSerializer):
    """Module with lessons for course detail"""
    lessons = LessonListSerializer(many=True, read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'lessons', 'lesson_count']

    def get_lesson_count(self, obj):
        return obj.lessons.count()


class CourseDetailSerializer(serializers.ModelSerializer):
    """Full course details with modules and lessons"""
    published_by = TeacherBasicSerializer(read_only=True)
    modules = ModuleListSerializer(many=True, read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    total_lessons = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    enrollment = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'published_by',
            'published_date',
            'price',
            'is_paid',
            'num_enrollments',
            'tags',
            'modules',
            'total_lessons',
            'is_enrolled',
            'enrollment',
        ]

    def get_total_lessons(self, obj):
        total = 0
        for module in obj.modules.all():
            total += module.lessons.count()
        return total

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False

    def get_enrollment(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            enrollment = Enrollment.objects.filter(
                user=request.user,
                course=obj
            ).first()
            if enrollment:
                return EnrollmentSerializer(enrollment).data
        return None


# ===== Learning & Lesson Serializers =====

class VideoLessonDetailSerializer(serializers.ModelSerializer):
    """Video lesson with file URL"""
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = VideoLesson
        fields = ['id', 'video_file', 'video_url', 'transcript']

    def get_video_url(self, obj):
        if obj.video_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video_file.url)
            return obj.video_file.url
        return None


class BlogLessonDetailSerializer(serializers.ModelSerializer):
    """Blog lesson with content and images"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = BlogLesson
        fields = ['id', 'content', 'images', 'image_url']

    def get_image_url(self, obj):
        if obj.images:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.images.url)
            return obj.images.url
        return None


class LessonDetailSerializer(serializers.ModelSerializer):
    """Full lesson details with video or blog content"""
    video = VideoLessonDetailSerializer(read_only=True)
    blog = BlogLessonDetailSerializer(read_only=True)
    is_completed = serializers.SerializerMethodField()
    module_id = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id',
            'title',
            'lesson_type',
            'duration',
            'created_at',
            'video',
            'blog',
            'is_completed',
            'module_id',
        ]

    def get_is_completed(self, obj):
        request = self.context.get('request')
        enrollment = self.context.get('enrollment')
        if enrollment:
            return CompletedLesson.objects.filter(
                enrollment=enrollment,
                lesson=obj
            ).exists()
        return False

    def get_module_id(self, obj):
        # Get module_id from context if available
        return self.context.get('module_id')


class VideoProgressSerializer(serializers.ModelSerializer):
    """Video playback progress"""
    class Meta:
        model = VideoProgress
        fields = [
            'id',
            'lesson',
            'last_position_seconds',
            'completed_percentage',
            'last_updated',
        ]
        read_only_fields = ['id', 'last_updated']


class SaveVideoProgressSerializer(serializers.Serializer):
    """Serializer for saving video progress"""
    lesson_id = serializers.IntegerField()
    current_time = serializers.FloatField(min_value=0)
    duration = serializers.FloatField(min_value=0)

    def validate(self, attrs):
        if attrs['current_time'] > attrs['duration']:
            raise serializers.ValidationError("Current time cannot be greater than duration")
        return attrs


class CompletedLessonSerializer(serializers.ModelSerializer):
    """Completed lesson record"""
    class Meta:
        model = CompletedLesson
        fields = ['id', 'lesson', 'completed_at']
        read_only_fields = ['id', 'completed_at']


class LearningProgressSerializer(serializers.Serializer):
    """Learning progress for a course"""
    course = CourseListSerializer(read_only=True)
    enrollment = EnrollmentSerializer(read_only=True)
    modules = serializers.SerializerMethodField()
    completed_lesson_ids = serializers.ListField(child=serializers.IntegerField())
    current_lesson = LessonDetailSerializer(read_only=True)
    previous_lesson = LessonDetailSerializer(read_only=True, allow_null=True)
    next_lesson = LessonDetailSerializer(read_only=True, allow_null=True)

    def get_modules(self, obj):
        return ModuleListSerializer(obj.get('modules', []), many=True).data


# ===== Certificate Serializers =====

class CertificateSerializer(serializers.Serializer):
    """Certificate data"""
    course = CourseListSerializer(read_only=True)
    enrollment = EnrollmentSerializer(read_only=True)
    student_name = serializers.CharField()
    completion_date = serializers.DateTimeField()
    certificate_id = serializers.CharField()


# ===== Discussion Serializers =====

class DiscussionUserSerializer(serializers.ModelSerializer):
    """User info for discussions"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'profile_picture', 'role']

    def get_full_name(self, obj):
        return obj.get_full_name()


class DiscussionReplySerializer(serializers.ModelSerializer):
    """Reply to a discussion post"""
    user = DiscussionUserSerializer(read_only=True)
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = DiscussionPost
        fields = [
            'id',
            'user',
            'content',
            'created_at',
            'updated_at',
            'is_edited',
            'edited_at',
            'can_edit',
            'can_delete',
        ]

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_edit(request.user)
        return False

    def get_can_delete(self, obj):
        request = self.context.get('request')
        course = self.context.get('course')
        if request and request.user.is_authenticated:
            return obj.can_delete(request.user, course)
        return False


class DiscussionPostSerializer(serializers.ModelSerializer):
    """Discussion post with nested replies"""
    user = DiscussionUserSerializer(read_only=True)
    replies = DiscussionReplySerializer(many=True, read_only=True)
    reply_count = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    can_pin = serializers.SerializerMethodField()

    class Meta:
        model = DiscussionPost
        fields = [
            'id',
            'user',
            'content',
            'created_at',
            'updated_at',
            'is_pinned',
            'is_edited',
            'edited_at',
            'replies',
            'reply_count',
            'can_edit',
            'can_delete',
            'can_pin',
        ]

    def get_reply_count(self, obj):
        return obj.get_reply_count()

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_edit(request.user)
        return False

    def get_can_delete(self, obj):
        request = self.context.get('request')
        course = self.context.get('course')
        if request and request.user.is_authenticated:
            return obj.can_delete(request.user, course)
        return False

    def get_can_pin(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_pin(request.user)
        return False


class DiscussionPostCreateSerializer(serializers.ModelSerializer):
    """Create a new discussion post"""
    class Meta:
        model = DiscussionPost
        fields = ['content']

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be empty")
        if len(value) > 5000:
            raise serializers.ValidationError("Content cannot exceed 5000 characters")
        return value


class DiscussionReplyCreateSerializer(serializers.ModelSerializer):
    """Create a reply to a discussion post"""
    class Meta:
        model = DiscussionPost
        fields = ['content']

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be empty")
        if len(value) > 5000:
            raise serializers.ValidationError("Content cannot exceed 5000 characters")
        return value
