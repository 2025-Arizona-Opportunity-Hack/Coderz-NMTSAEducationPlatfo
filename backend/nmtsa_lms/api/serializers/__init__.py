"""
API Serializers for NMTSA LMS
Maps Django models to JSON representations for the REST API
"""
from rest_framework import serializers
from authentication.models import User, TeacherProfile, StudentProfile, Enrollment
from teacher_dash.models import Course, Module, Lesson, VideoLesson, BlogLesson, DiscussionPost
from lms.models import CompletedLesson, VideoProgress, ForumPost, ForumComment, ForumLike


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer - maps to Profile type in frontend
    """
    fullName = serializers.SerializerMethodField()
    avatarUrl = serializers.URLField(source='profile_picture', allow_null=True, required=False)
    createdAt = serializers.DateTimeField(source='date_joined', read_only=True)
    updatedAt = serializers.DateTimeField(source='last_login', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'fullName', 'role', 'avatarUrl', 'createdAt', 'updatedAt']
        read_only_fields = ['id', 'createdAt', 'updatedAt']
    
    def get_fullName(self, obj):
        return obj.get_full_name() or obj.username


class TeacherProfileSerializer(serializers.ModelSerializer):
    """Teacher profile with credentials"""
    class Meta:
        model = TeacherProfile
        fields = ['bio', 'credentials', 'specialization', 'years_experience', 
                  'verification_status', 'resume', 'certifications']


class InstructorSerializer(serializers.ModelSerializer):
    """
    Instructor info for course display
    """
    fullName = serializers.SerializerMethodField()
    avatarUrl = serializers.URLField(source='profile_picture', allow_null=True, required=False)
    bio = serializers.SerializerMethodField()
    credentials = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'fullName', 'avatarUrl', 'bio', 'credentials']
    
    def get_fullName(self, obj):
        return obj.get_full_name() or obj.username
    
    def get_bio(self, obj):
        try:
            return obj.teacher_profile.bio
        except:
            return ""
    
    def get_credentials(self, obj):
        try:
            return obj.teacher_profile.credentials
        except:
            return ""


class LessonSerializer(serializers.ModelSerializer):
    """
    Lesson serializer with type and content info
    """
    type = serializers.CharField(source='lesson_type')
    order = serializers.IntegerField(default=0)
    isCompleted = serializers.SerializerMethodField()
    isLocked = serializers.SerializerMethodField()
    contentUrl = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'lesson_type', 'type', 'duration', 'order', 
                  'isCompleted', 'isLocked', 'contentUrl', 'created_at']
    
    def get_isCompleted(self, obj):
        # Will be set from context if enrollment is provided
        return self.context.get('completed_lessons', set()).__contains__(obj.id)
    
    def get_isLocked(self, obj):
        # For now, no lessons are locked
        return False
    
    def get_contentUrl(self, obj):
        if obj.lesson_type == 'video' and hasattr(obj, 'video'):
            return obj.video.video_file.url if obj.video.video_file else None
        return None


class ModuleSerializer(serializers.ModelSerializer):
    """
    Module serializer with lessons
    """
    lessons = LessonSerializer(many=True, read_only=True)
    isCompleted = serializers.SerializerMethodField()
    order = serializers.IntegerField(default=0)
    
    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'order', 'lessons', 'isCompleted']
    
    def get_isCompleted(self, obj):
        # Module is complete if all lessons are complete
        completed = self.context.get('completed_lessons', set())
        module_lessons = obj.lessons.all()
        if not module_lessons:
            return False
        return all(lesson.id in completed for lesson in module_lessons)


class CourseSerializer(serializers.ModelSerializer):
    """
    Basic course serializer for list views
    """
    instructor = InstructorSerializer(source='published_by', read_only=True)
    instructorId = serializers.IntegerField(source='published_by_id', read_only=True)
    thumbnailUrl = serializers.URLField(source='thumbnail_url', allow_null=True, required=False)
    difficulty = serializers.CharField(default='beginner')
    duration = serializers.SerializerMethodField()
    credits = serializers.IntegerField(default=0)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, allow_null=True, required=False)
    enrollmentCount = serializers.IntegerField(source='num_enrollments', read_only=True)
    createdAt = serializers.DateTimeField(source='published_date', read_only=True)
    updatedAt = serializers.DateTimeField(source='published_date', read_only=True)
    category = serializers.CharField(default='General')
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'thumbnailUrl', 'instructor', 'instructorId',
                  'category', 'difficulty', 'duration', 'credits', 'rating', 
                  'enrollmentCount', 'createdAt', 'updatedAt', 'price', 'is_paid']
    
    def get_duration(self, obj):
        # Calculate total duration from all lessons in all modules
        total = 0
        for module in obj.modules.all():
            for lesson in module.lessons.all():
                if lesson.duration:
                    total += lesson.duration
        return total


class CourseDetailSerializer(CourseSerializer):
    """
    Detailed course serializer with modules and reviews
    """
    longDescription = serializers.CharField(source='long_description', allow_null=True, required=False)
    prerequisites = serializers.JSONField(default=list)
    learningObjectives = serializers.JSONField(source='learning_objectives', default=list)
    modules = ModuleSerializer(many=True, read_only=True)
    isEnrolled = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    averageRating = serializers.DecimalField(source='rating', max_digits=3, decimal_places=2, 
                                             allow_null=True, required=False)
    totalReviews = serializers.IntegerField(default=0)
    
    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + [
            'longDescription', 'prerequisites', 'learningObjectives', 'modules',
            'isEnrolled', 'progress', 'averageRating', 'totalReviews'
        ]
    
    def get_isEnrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(
                user=request.user,
                course=obj,
                is_active=True
            ).exists()
        return False
    
    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                enrollment = Enrollment.objects.get(
                    user=request.user,
                    course=obj,
                    is_active=True
                )
                return enrollment.progress_percentage
            except Enrollment.DoesNotExist:
                return 0
        return 0


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Enrollment serializer
    """
    userId = serializers.IntegerField(source='user_id', read_only=True)
    courseId = serializers.IntegerField(source='course_id', read_only=True)
    progress = serializers.IntegerField(source='progress_percentage')
    completedLessons = serializers.SerializerMethodField()
    enrolledAt = serializers.DateTimeField(source='enrolled_at', read_only=True)
    completedAt = serializers.DateTimeField(source='completed_at', allow_null=True, required=False)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'userId', 'courseId', 'progress', 'completedLessons', 
                  'enrolledAt', 'completedAt']
    
    def get_completedLessons(self, obj):
        return list(
            CompletedLesson.objects.filter(enrollment=obj)
            .values_list('lesson_id', flat=True)
        )


class EnrollmentWithProgressSerializer(EnrollmentSerializer):
    """
    Enrollment with course info and progress
    """
    course = CourseSerializer(read_only=True)
    lastAccessedAt = serializers.DateTimeField(source='last_accessed_at', allow_null=True, required=False)
    currentLesson = serializers.SerializerMethodField()
    
    class Meta(EnrollmentSerializer.Meta):
        fields = EnrollmentSerializer.Meta.fields + ['course', 'lastAccessedAt', 'currentLesson']
    
    def get_currentLesson(self, obj):
        if obj.current_lesson:
            return {
                'id': str(obj.current_lesson.id),
                'title': obj.current_lesson.title,
                'moduleTitle': obj.current_lesson.module_set.first().title if obj.current_lesson.module_set.exists() else ''
            }
        return None


class LessonProgressSerializer(serializers.ModelSerializer):
    """
    Lesson progress tracking
    """
    lessonId = serializers.IntegerField(source='lesson_id')
    courseId = serializers.SerializerMethodField()
    isCompleted = serializers.SerializerMethodField()
    timeSpent = serializers.IntegerField(default=0)
    lastPosition = serializers.SerializerMethodField()
    completedAt = serializers.DateTimeField(source='completed_at', allow_null=True, required=False)
    
    class Meta:
        model = CompletedLesson
        fields = ['lessonId', 'courseId', 'isCompleted', 'timeSpent', 'lastPosition', 'completedAt']
    
    def get_courseId(self, obj):
        return str(obj.enrollment.course_id)
    
    def get_isCompleted(self, obj):
        return True  # CompletedLesson means it's completed
    
    def get_lastPosition(self, obj):
        # Get video progress if it's a video lesson
        try:
            video_progress = VideoProgress.objects.get(
                enrollment=obj.enrollment,
                lesson=obj.lesson
            )
            return video_progress.last_position_seconds
        except VideoProgress.DoesNotExist:
            return 0


class ForumAuthorSerializer(serializers.ModelSerializer):
    """Serializer for forum post/comment author info"""
    fullName = serializers.SerializerMethodField()
    avatarUrl = serializers.URLField(source='profile_picture', allow_null=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'fullName', 'avatarUrl', 'role']
    
    def get_fullName(self, obj):
        return obj.get_full_name() or obj.username


class ForumCommentSerializer(serializers.ModelSerializer):
    """Serializer for forum comments"""
    postId = serializers.CharField(source='post_id', read_only=True)
    authorId = serializers.CharField(source='author_id', read_only=True)
    author = ForumAuthorSerializer(read_only=True)
    parentId = serializers.CharField(source='parent_id', required=False, allow_null=True)
    replies = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    isLiked = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    
    class Meta:
        model = ForumComment
        fields = ['id', 'postId', 'content', 'authorId', 'author', 'parentId', 
                  'replies', 'likes', 'isLiked', 'createdAt', 'updatedAt']
        read_only_fields = ['id', 'postId', 'authorId', 'author', 'createdAt', 'updatedAt']
    
    def get_replies(self, obj):
        # Get direct replies only (not nested)
        replies = obj.replies.all()
        return ForumCommentSerializer(replies, many=True, context=self.context).data
    
    def get_likes(self, obj):
        return obj.get_likes_count()
    
    def get_isLiked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ForumLike.objects.filter(user=request.user, comment=obj).exists()
        return False


class ForumPostSerializer(serializers.ModelSerializer):
    """Serializer for forum posts"""
    authorId = serializers.CharField(source='author_id', read_only=True)
    author = ForumAuthorSerializer(read_only=True)
    excerpt = serializers.ReadOnlyField()
    commentsCount = serializers.IntegerField(source='comments_count', read_only=True)
    likes = serializers.SerializerMethodField()
    isLiked = serializers.SerializerMethodField()
    isPinned = serializers.BooleanField(source='is_pinned', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    
    class Meta:
        model = ForumPost
        fields = ['id', 'title', 'content', 'excerpt', 'authorId', 'author', 'tags',
                  'likes', 'commentsCount', 'isLiked', 'isPinned', 'createdAt', 'updatedAt']
        read_only_fields = ['id', 'authorId', 'author', 'excerpt', 'createdAt', 'updatedAt']
    
    def get_likes(self, obj):
        return obj.get_likes_count()
    
    def get_isLiked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ForumLike.objects.filter(user=request.user, post=obj).exists()
        return False


# ============================================================================
# PROFILE & ONBOARDING SERIALIZERS
# ============================================================================

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


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for complete user profile with role-specific data"""
    teacher_profile = TeacherProfileSerializer(read_only=True)
    student_profile = serializers.SerializerMethodField()
    
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
    
    def get_student_profile(self, obj):
        if hasattr(obj, 'student_profile'):
            return {
                'relationship': obj.student_profile.relationship,
                'care_recipient_name': obj.student_profile.care_recipient_name,
                'care_recipient_age': obj.student_profile.care_recipient_age,
                'special_needs': obj.student_profile.special_needs,
                'learning_goals': obj.student_profile.learning_goals,
                'interests': obj.student_profile.interests,
                'accessibility_needs': obj.student_profile.accessibility_needs,
            }
        return None
