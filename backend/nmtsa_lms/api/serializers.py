"""
API Serializers for NMTSA LMS
Maps Django models to JSON representations for the REST API
"""
from rest_framework import serializers
from authentication.models import User, TeacherProfile, StudentProfile, Enrollment
from teacher_dash.models import Course, Module, Lesson, VideoLesson, BlogLesson, DiscussionPost
from lms.models import CompletedLesson, VideoProgress


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
