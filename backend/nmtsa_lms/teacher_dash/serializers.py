"""
Serializers for teacher dashboard
Handles course management, modules, lessons, and analytics
"""

from rest_framework import serializers
from authentication.models import TeacherProfile
from teacher_dash.models import Course, Module, Lesson, VideoLesson, BlogLesson, DiscussionPost
from lms.models import CompletedLesson
from taggit.serializers import TagListSerializerField, TaggitSerializer


# ===== Dashboard & Statistics =====

class TeacherDashboardStatsSerializer(serializers.Serializer):
    """Dashboard statistics for teacher"""
    course_count = serializers.IntegerField()
    published_count = serializers.IntegerField()
    draft_count = serializers.IntegerField()
    verification_status = serializers.CharField()
    is_teacher_approved = serializers.BooleanField()
    awaiting_review_count = serializers.IntegerField()
    approved_not_published_count = serializers.IntegerField()
    not_submitted_count = serializers.IntegerField()


# ===== Course Serializers =====

class TeacherCourseListSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Course list for teacher dashboard"""
    tags = TagListSerializerField(required=False)
    module_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'published_date',
            'is_published',
            'is_submitted_for_review',
            'admin_approved',
            'admin_review_feedback',
            'price',
            'is_paid',
            'num_enrollments',
            'tags',
            'module_count',
        ]

    def get_module_count(self, obj) -> int:
        return obj.modules.count()


class CourseCreateSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Create a new course"""
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'is_paid', 'tags']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value

    def create(self, validated_data):
        # Extract teacher from context
        teacher = self.context['request'].user
        validated_data['published_by'] = teacher
        return super().create(validated_data)


class CourseUpdateSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Update course information"""
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'is_paid', 'tags']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value


# ===== Module Serializers =====

class TeacherLessonBasicSerializer(serializers.ModelSerializer):
    """Basic lesson info for module details (Teacher Dashboard)"""
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'lesson_type', 'duration', 'created_at']


class ModuleListSerializer(serializers.ModelSerializer):
    """Module with lesson count"""
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'lesson_count']

    def get_lesson_count(self, obj) -> int:
        return obj.lessons.count()


class ModuleDetailSerializer(serializers.ModelSerializer):
    """Module with full lesson list"""
    lessons = TeacherLessonBasicSerializer(many=True, read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'lessons', 'lesson_count']

    def get_lesson_count(self, obj) -> int:
        return obj.lessons.count()


class ModuleCreateSerializer(serializers.ModelSerializer):
    """Create a new module"""
    class Meta:
        model = Module
        fields = ['title', 'description']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value


class ModuleUpdateSerializer(serializers.ModelSerializer):
    """Update module information"""
    class Meta:
        model = Module
        fields = ['title', 'description']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value


# ===== Lesson Serializers =====

class VideoLessonSerializer(serializers.ModelSerializer):
    """Video lesson with file upload"""
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = VideoLesson
        fields = ['id', 'video_file', 'video_url', 'transcript']

    def get_video_url(self, obj) -> str | None:
        if obj.video_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video_file.url)
            return obj.video_file.url
        return None


class BlogLessonSerializer(serializers.ModelSerializer):
    """Blog lesson with content and images"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = BlogLesson
        fields = ['id', 'content', 'images', 'image_url']

    def get_image_url(self, obj) -> str | None:
        if obj.images:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.images.url)
            return obj.images.url
        return None


class LessonDetailSerializer(serializers.ModelSerializer):
    """Full lesson details with video or blog content"""
    video = VideoLessonSerializer(read_only=True)
    blog = BlogLessonSerializer(read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'lesson_type', 'duration', 'created_at', 'video', 'blog']


class LessonCreateSerializer(serializers.ModelSerializer):
    """Create a new lesson (base data)"""
    # Video lesson fields
    video_file = serializers.FileField(required=False, write_only=True)
    transcript = serializers.CharField(required=False, allow_blank=True, write_only=True)

    # Blog lesson fields
    content = serializers.CharField(required=False, allow_blank=True, write_only=True)
    images = serializers.ImageField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Lesson
        fields = ['title', 'lesson_type', 'duration', 'video_file', 'transcript', 'content', 'images']

    def validate(self, attrs):
        lesson_type = attrs.get('lesson_type')

        if lesson_type == 'video':
            if not attrs.get('video_file'):
                raise serializers.ValidationError({"video_file": "Video file is required for video lessons"})
        elif lesson_type == 'blog':
            if not attrs.get('content'):
                raise serializers.ValidationError({"content": "Content is required for blog lessons"})

        return attrs

    def validate_video_file(self, value):
        if value:
            # Check file size (max 500MB)
            if value.size > 500 * 1024 * 1024:
                raise serializers.ValidationError("Video file size cannot exceed 500MB")
            # Check file extension
            import os
            ext = os.path.splitext(value.name)[1].lower()
            allowed = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
            if ext not in allowed:
                raise serializers.ValidationError(f"Video must be one of: {', '.join(allowed)}")
        return value

    def validate_images(self, value):
        if value:
            # Check file size (max 10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("Image file size cannot exceed 10MB")
        return value


class LessonUpdateSerializer(serializers.ModelSerializer):
    """Update lesson information"""
    # Video lesson fields
    video_file = serializers.FileField(required=False, write_only=True)
    transcript = serializers.CharField(required=False, allow_blank=True, write_only=True)

    # Blog lesson fields
    content = serializers.CharField(required=False, allow_blank=True, write_only=True)
    images = serializers.ImageField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Lesson
        fields = ['title', 'lesson_type', 'duration', 'video_file', 'transcript', 'content', 'images']

    def validate_video_file(self, value):
        if value:
            if value.size > 500 * 1024 * 1024:
                raise serializers.ValidationError("Video file size cannot exceed 500MB")
            import os
            ext = os.path.splitext(value.name)[1].lower()
            allowed = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
            if ext not in allowed:
                raise serializers.ValidationError(f"Video must be one of: {', '.join(allowed)}")
        return value

    def validate_images(self, value):
        if value:
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("Image file size cannot exceed 10MB")
        return value


# ===== Course Detail & Preview =====

class TeacherCourseDetailSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Full course details for teacher view"""
    modules = ModuleDetailSerializer(many=True, read_only=True)
    tags = TagListSerializerField(required=False)
    module_count = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'published_date',
            'is_published',
            'is_submitted_for_review',
            'admin_approved',
            'admin_review_feedback',
            'price',
            'is_paid',
            'num_enrollments',
            'tags',
            'modules',
            'module_count',
            'total_lessons',
        ]

    def get_module_count(self, obj) -> int:
        return obj.modules.count()

    def get_total_lessons(self, obj) -> int:
        total = 0
        for module in obj.modules.all():
            total += module.lessons.count()
        return total


# ===== Analytics =====

class CourseAnalyticsSerializer(serializers.Serializer):
    """Course analytics data"""
    course = TeacherCourseListSerializer(read_only=True)
    enrollments = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()


# ===== Publishing =====

class CoursePublishSerializer(serializers.Serializer):
    """Course publish action"""
    # No fields needed, just an action endpoint
    pass


class CourseUnpublishSerializer(serializers.Serializer):
    """Course unpublish action"""
    # No fields needed, just an action endpoint
    pass


# ===== Discussion Serializers =====

class DiscussionUserSerializer(serializers.Serializer):
    """User info for discussions"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    profile_picture = serializers.URLField(allow_null=True)
    role = serializers.CharField()


class DiscussionReplySerializer(serializers.ModelSerializer):
    """Reply to a discussion post"""
    user = serializers.SerializerMethodField()

    class Meta:
        model = DiscussionPost
        fields = ['id', 'user', 'content', 'created_at', 'updated_at', 'is_edited', 'edited_at']

    def get_user(self, obj) -> dict:
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'full_name': obj.user.get_full_name(),
            'profile_picture': obj.user.profile_picture,
            'role': obj.user.role,
        }


class TeacherDiscussionPostSerializer(serializers.ModelSerializer):
    """Discussion post for teacher view (Teacher Dashboard)"""
    user = serializers.SerializerMethodField()
    replies = DiscussionReplySerializer(many=True, read_only=True)
    reply_count = serializers.SerializerMethodField()

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
        ]

    def get_user(self, obj) -> dict:
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'full_name': obj.user.get_full_name(),
            'profile_picture': obj.user.profile_picture,
            'role': obj.user.role,
        }

    def get_reply_count(self, obj) -> int:
        return obj.get_reply_count()


class DiscussionPostCreateSerializer(serializers.ModelSerializer):
    """Create discussion post"""
    class Meta:
        model = DiscussionPost
        fields = ['content']

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be empty")
        
        # Minimum length validation (matching forms.py)
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Your post must be at least 10 characters long.")
        
        # Maximum length validation (matching forms.py)
        if len(value) > 2000:
            raise serializers.ValidationError("Your post must be no more than 2000 characters long.")
        
        return value
