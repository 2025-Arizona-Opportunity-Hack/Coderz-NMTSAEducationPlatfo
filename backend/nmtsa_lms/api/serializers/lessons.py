"""
Lesson Content and Progress Serializers
Handles lesson viewing, completion, and progress tracking
"""
from rest_framework import serializers
from teacher_dash.models import Lesson, VideoLesson, BlogLesson, Module, Course
from lms.models import CompletedLesson, VideoProgress
from authentication.models import Enrollment


class VideoLessonDetailSerializer(serializers.ModelSerializer):
    """Detailed video lesson with file URL and transcript"""
    video_url = serializers.SerializerMethodField()
    
    class Meta:
        model = VideoLesson
        fields = ['video_url', 'transcript']
    
    def get_video_url(self, obj):
        request = self.context.get('request')
        if obj.video_file:
            if request:
                return request.build_absolute_uri(obj.video_file.url)
            return obj.video_file.url
        return None


class BlogLessonDetailSerializer(serializers.ModelSerializer):
    """Detailed blog lesson with HTML content and images"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogLesson
        fields = ['content', 'image_url']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.images:
            if request:
                return request.build_absolute_uri(obj.images.url)
            return obj.images.url
        return None


class LessonNavigationSerializer(serializers.ModelSerializer):
    """Simplified lesson info for navigation"""
    type = serializers.CharField(source='lesson_type')
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'type', 'duration']


class LessonContentSerializer(serializers.ModelSerializer):
    """
    Complete lesson content with video/blog data, navigation, and progress
    """
    type = serializers.CharField(source='lesson_type')
    video = VideoLessonDetailSerializer(read_only=True)
    blog = BlogLessonDetailSerializer(read_only=True)
    next_lesson = serializers.SerializerMethodField()
    previous_lesson = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    last_position = serializers.SerializerMethodField()
    module_id = serializers.SerializerMethodField()
    module_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'lesson_type', 'type', 'duration', 'description',
            'video', 'blog', 'next_lesson', 'previous_lesson',
            'is_completed', 'last_position', 'module_id', 'module_title'
        ]
    
    def get_module_id(self, obj):
        """Get the module ID this lesson belongs to"""
        module = obj.module_set.first()
        return str(module.id) if module else None
    
    def get_module_title(self, obj):
        """Get the module title this lesson belongs to"""
        module = obj.module_set.first()
        return module.title if module else None
    
    def get_next_lesson(self, obj):
        """Get the next lesson in sequence"""
        course_id = self.context.get('course_id')
        if not course_id:
            return None
        
        try:
            course = Course.objects.get(id=course_id)
            modules = course.modules.all().order_by('order', 'id')
            
            # Find current lesson's module
            current_module = obj.module_set.first()
            if not current_module:
                return None
            
            # Get lessons in current module
            current_module_lessons = list(current_module.lessons.all().order_by('order', 'id'))
            
            try:
                current_index = current_module_lessons.index(obj)
                # Try next lesson in same module
                if current_index < len(current_module_lessons) - 1:
                    next_lesson = current_module_lessons[current_index + 1]
                    return LessonNavigationSerializer(next_lesson).data
            except ValueError:
                pass
            
            # Try first lesson of next module
            module_list = list(modules)
            try:
                current_module_index = module_list.index(current_module)
                if current_module_index < len(module_list) - 1:
                    next_module = module_list[current_module_index + 1]
                    first_lesson = next_module.lessons.first()
                    if first_lesson:
                        return LessonNavigationSerializer(first_lesson).data
            except ValueError:
                pass
                
        except Course.DoesNotExist:
            pass
        
        return None
    
    def get_previous_lesson(self, obj):
        """Get the previous lesson in sequence"""
        course_id = self.context.get('course_id')
        if not course_id:
            return None
        
        try:
            course = Course.objects.get(id=course_id)
            modules = course.modules.all().order_by('order', 'id')
            
            # Find current lesson's module
            current_module = obj.module_set.first()
            if not current_module:
                return None
            
            # Get lessons in current module
            current_module_lessons = list(current_module.lessons.all().order_by('order', 'id'))
            
            try:
                current_index = current_module_lessons.index(obj)
                # Try previous lesson in same module
                if current_index > 0:
                    prev_lesson = current_module_lessons[current_index - 1]
                    return LessonNavigationSerializer(prev_lesson).data
            except ValueError:
                pass
            
            # Try last lesson of previous module
            module_list = list(modules)
            try:
                current_module_index = module_list.index(current_module)
                if current_module_index > 0:
                    prev_module = module_list[current_module_index - 1]
                    last_lesson = prev_module.lessons.last()
                    if last_lesson:
                        return LessonNavigationSerializer(last_lesson).data
            except ValueError:
                pass
                
        except Course.DoesNotExist:
            pass
        
        return None
    
    def get_is_completed(self, obj):
        """Check if lesson is completed by current user"""
        request = self.context.get('request')
        course_id = self.context.get('course_id')
        
        if not request or not request.user.is_authenticated or not course_id:
            return False
        
        try:
            enrollment = Enrollment.objects.get(
                user=request.user,
                course_id=course_id,
                is_active=True
            )
            return CompletedLesson.objects.filter(
                enrollment=enrollment,
                lesson=obj
            ).exists()
        except Enrollment.DoesNotExist:
            return False
    
    def get_last_position(self, obj):
        """Get last video position for video lessons"""
        request = self.context.get('request')
        course_id = self.context.get('course_id')
        
        if (not request or not request.user.is_authenticated or 
            not course_id or obj.lesson_type != 'video'):
            return 0
        
        try:
            enrollment = Enrollment.objects.get(
                user=request.user,
                course_id=course_id,
                is_active=True
            )
            video_progress = VideoProgress.objects.get(
                enrollment=enrollment,
                lesson=obj
            )
            return video_progress.last_position_seconds
        except (Enrollment.DoesNotExist, VideoProgress.DoesNotExist):
            return 0


class LessonCompletionSerializer(serializers.Serializer):
    """Response after marking lesson complete"""
    lesson_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    is_completed = serializers.BooleanField()
    completed_at = serializers.DateTimeField()
    progress = serializers.DictField()


class VideoProgressUpdateSerializer(serializers.Serializer):
    """Update video playback progress"""
    last_position_seconds = serializers.IntegerField(min_value=0)
    completed_percentage = serializers.IntegerField(min_value=0, max_value=100)


class CertificateSerializer(serializers.ModelSerializer):
    """Certificate information for completed course"""
    course_id = serializers.IntegerField(source='course.id')
    user_id = serializers.IntegerField(source='user.id')
    course_title = serializers.CharField(source='course.title')
    instructor_name = serializers.SerializerMethodField()
    certificate_number = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course_id', 'user_id', 'course_title',
            'instructor_name', 'completed_at', 'certificate_number',
            'download_url'
        ]
    
    def get_instructor_name(self, obj):
        return obj.course.published_by.get_full_name() or obj.course.published_by.username
    
    def get_certificate_number(self, obj):
        """Generate certificate number"""
        return f"NMTSA-{obj.completed_at.year}-{obj.id:06d}"
    
    def get_download_url(self, obj):
        """Get certificate PDF download URL"""
        request = self.context.get('request')
        url = f"/api/certificates/{obj.id}/pdf"
        if request:
            return request.build_absolute_uri(url)
        return url
