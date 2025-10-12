"""
API views for teacher dashboard
Handles course management, modules, lessons, publishing, and analytics
"""

import os
import math
import tempfile
import uuid
from pathlib import Path
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, FileResponse
from django.db import transaction
from django.utils import timezone
from django.core.mail import mail_admins
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiResponse

from authentication.models import TeacherProfile
from authentication.permissions import IsTeacher, IsTeacherVerified, IsOnboardingComplete
from teacher_dash.permissions import IsCourseOwner, IsModuleOwner, IsLessonOwner
from teacher_dash.models import Course, Module, Lesson, VideoLesson, BlogLesson, DiscussionPost
from lms.models import CompletedLesson
from .serializers import (
    TeacherDashboardStatsSerializer,
    TeacherCourseListSerializer,
    TeacherCourseDetailSerializer,
    CourseCreateSerializer,
    CourseUpdateSerializer,
    ModuleListSerializer,
    ModuleDetailSerializer,
    ModuleCreateSerializer,
    ModuleUpdateSerializer,
    LessonDetailSerializer,
    LessonCreateSerializer,
    LessonUpdateSerializer,
    CourseAnalyticsSerializer,
    TeacherDiscussionPostSerializer,
    DiscussionPostCreateSerializer,
)


# ===== Helper Functions =====

def _generate_uuid_filename(original_filename):
    """
    Generate a unique filename using UUID while preserving the file extension.
    This prevents filename collisions and information disclosure.
    """
    ext = Path(original_filename).suffix or '.mp4'
    return f"{uuid.uuid4()}{ext}"


# ===== Dashboard =====

class TeacherDashboardView(APIView):
    """
    GET /api/v1/teacher/dashboard/
    Returns teacher dashboard statistics
    """
    permission_classes = [IsTeacher, IsOnboardingComplete]

    @extend_schema(
        operation_id='teacher_dashboard',
        responses={200: TeacherDashboardStatsSerializer},
        description="Get teacher dashboard statistics including course counts and verification status"
    )
    def get(self, request):
        teacher = request.user
        courses = Course.objects.filter(published_by=teacher).prefetch_related('modules', 'modules__lessons')

        published = courses.filter(is_published=True)
        drafts = courses.filter(is_published=False)

        teacher_profile = TeacherProfile.objects.filter(user=teacher).first()
        is_teacher_approved = teacher_profile and teacher_profile.verification_status == 'approved'

        # Group courses by review status
        awaiting_review = drafts.filter(is_submitted_for_review=True, admin_approved=False)
        approved_not_published = drafts.filter(admin_approved=True, is_submitted_for_review=True)
        not_submitted = drafts.filter(is_submitted_for_review=False)

        data = {
            'course_count': courses.count(),
            'published_count': published.count(),
            'draft_count': drafts.count(),
            'verification_status': getattr(teacher_profile, 'verification_status', 'pending'),
            'is_teacher_approved': is_teacher_approved,
            'awaiting_review_count': awaiting_review.count(),
            'approved_not_published_count': approved_not_published.count(),
            'not_submitted_count': not_submitted.count(),
        }

        serializer = TeacherDashboardStatsSerializer(data)
        return Response(serializer.data)


class VerificationStatusView(APIView):
    """
    GET /api/v1/teacher/verification/
    Returns teacher verification status and profile
    """
    permission_classes = [IsTeacher, IsOnboardingComplete]

    def get(self, request):
        teacher = request.user
        profile = TeacherProfile.objects.filter(user=teacher).first()

        if not profile:
            return Response(
                {'error': 'Teacher profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'verification_status': profile.verification_status,
            'verification_notes': profile.verification_notes,
            'verified_at': profile.verified_at,
            'specialization': profile.specialization,
            'years_experience': profile.years_experience,
        })


# ===== Course Management =====

class TeacherCoursesView(ListAPIView):
    """
    GET /api/v1/teacher/courses/
    Returns paginated list of teacher's courses
    """
    permission_classes = [IsTeacher, IsOnboardingComplete]
    serializer_class = TeacherCourseListSerializer

    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Course.objects.none()
        
        return Course.objects.filter(
            published_by=self.request.user
        ).prefetch_related('modules', 'modules__lessons').order_by('-published_date')


class CourseCreateView(APIView):
    """
    POST /api/v1/teacher/courses/
    Create a new course
    """
    permission_classes = [IsTeacher, IsTeacherVerified, IsOnboardingComplete]

    def post(self, request):
        serializer = CourseCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            course = serializer.save()
            return Response(
                {
                    'message': 'Course created successfully. You can now add modules and lessons.',
                    'course': TeacherCourseDetailSerializer(course).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseDetailView(RetrieveAPIView):
    """
    GET /api/v1/teacher/courses/{course_id}/
    Returns full course details with modules and lessons
    """
    permission_classes = [IsTeacher, IsOnboardingComplete, IsCourseOwner]
    serializer_class = TeacherCourseDetailSerializer
    lookup_url_kwarg = 'course_id'

    def get_queryset(self):
        return Course.objects.filter(
            published_by=self.request.user
        ).prefetch_related('modules', 'modules__lessons')


class CourseUpdateView(APIView):
    """
    PUT/PATCH /api/v1/teacher/courses/{course_id}/
    Update course information
    """
    permission_classes = [IsTeacher, IsTeacherVerified, IsOnboardingComplete, IsCourseOwner]

    def put(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        serializer = CourseUpdateSerializer(course, data=request.data, partial=False)

        if serializer.is_valid():
            serializer.save()

            # Handle course content change
            message = self._handle_course_content_change(course)

            return Response(
                {
                    'message': message,
                    'course': TeacherCourseDetailSerializer(course).data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        serializer = CourseUpdateSerializer(course, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            message = self._handle_course_content_change(course)

            return Response(
                {
                    'message': message,
                    'course': TeacherCourseDetailSerializer(course).data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _handle_course_content_change(self, course):
        """Handle workflow when content changes are made to published course"""
        if course.is_published:
            course.is_published = False
            course.is_submitted_for_review = True
            course.admin_approved = False
            course.save()
            return "Changes saved. The course is now unpublished and resubmitted for admin review. Enrollments and discussions remain intact."
        return "Changes saved successfully."


class CourseDeleteView(DestroyAPIView):
    """
    DELETE /api/v1/teacher/courses/{course_id}/
    Delete a course
    """
    permission_classes = [IsTeacher, IsTeacherVerified, IsOnboardingComplete, IsCourseOwner]
    lookup_url_kwarg = 'course_id'

    def get_queryset(self):
        return Course.objects.filter(published_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'Course deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )


# ===== Module Management =====

class ModuleListCreateView(APIView):
    """
    GET /api/v1/teacher/courses/{course_id}/modules/
    POST /api/v1/teacher/courses/{course_id}/modules/
    """
    permission_classes = [IsTeacher, IsOnboardingComplete, IsCourseOwner]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        modules = course.modules.all().prefetch_related('lessons')
        serializer = ModuleDetailSerializer(modules, many=True)
        return Response(serializer.data)

    def post(self, request, course_id):
        # Check teacher is verified
        teacher_profile = TeacherProfile.objects.filter(user=request.user).first()
        if not teacher_profile or teacher_profile.verification_status != 'approved':
            return Response(
                {'error': 'Your teacher profile must be approved to create modules.'},
                status=status.HTTP_403_FORBIDDEN
            )

        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        serializer = ModuleCreateSerializer(data=request.data)

        if serializer.is_valid():
            module = serializer.save()
            course.modules.add(module)

            message = self._handle_course_content_change(course)

            return Response(
                {
                    'message': message,
                    'module': ModuleDetailSerializer(module).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _handle_course_content_change(self, course):
        if course.is_published:
            course.is_published = False
            course.is_submitted_for_review = True
            course.admin_approved = False
            course.save()
            return "Module added. Course unpublished and resubmitted for review."
        return "Module added successfully."


class ModuleDetailView(RetrieveAPIView):
    """
    GET /api/v1/teacher/courses/{course_id}/modules/{module_id}/
    Returns module details with lessons
    """
    permission_classes = [IsTeacher, IsOnboardingComplete, IsModuleOwner]
    serializer_class = ModuleDetailSerializer
    lookup_url_kwarg = 'module_id'

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id, published_by=self.request.user)
        return course.modules.prefetch_related('lessons')


class ModuleUpdateView(APIView):
    """
    PUT/PATCH /api/v1/teacher/courses/{course_id}/modules/{module_id}/
    Update module information
    """
    permission_classes = [IsTeacher, IsTeacherVerified, IsOnboardingComplete, IsModuleOwner]

    def put(self, request, course_id, module_id):
        return self._update(request, course_id, module_id, partial=False)

    def patch(self, request, course_id, module_id):
        return self._update(request, course_id, module_id, partial=True)

    def _update(self, request, course_id, module_id, partial):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        module = get_object_or_404(course.modules, id=module_id)

        serializer = ModuleUpdateSerializer(module, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()

            message = self._handle_course_content_change(course)

            return Response(
                {
                    'message': message,
                    'module': ModuleDetailSerializer(module).data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _handle_course_content_change(self, course):
        if course.is_published:
            course.is_published = False
            course.is_submitted_for_review = True
            course.admin_approved = False
            course.save()
            return "Changes saved. Course unpublished and resubmitted for review."
        return "Changes saved successfully."


class ModuleDeleteView(APIView):
    """
    DELETE /api/v1/teacher/courses/{course_id}/modules/{module_id}/
    Delete a module
    """
    permission_classes = [IsTeacher, IsTeacherVerified, IsOnboardingComplete, IsModuleOwner]

    def delete(self, request, course_id, module_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        module = get_object_or_404(course.modules, id=module_id)

        course.modules.remove(module)
        module.delete()

        message = self._handle_course_content_change(course)

        return Response(
            {'message': message},
            status=status.HTTP_204_NO_CONTENT
        )

    def _handle_course_content_change(self, course):
        if course.is_published:
            course.is_published = False
            course.is_submitted_for_review = True
            course.admin_approved = False
            course.save()
            return "Module deleted. Course unpublished and resubmitted for review."
        return "Module deleted successfully."


# ===== Lesson Management =====

class LessonListCreateView(APIView):
    """
    GET /api/v1/teacher/courses/{course_id}/modules/{module_id}/lessons/
    POST /api/v1/teacher/courses/{course_id}/modules/{module_id}/lessons/
    """
    permission_classes = [IsTeacher, IsOnboardingComplete, IsModuleOwner]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, course_id, module_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        module = get_object_or_404(course.modules, id=module_id)
        lessons = module.lessons.all()
        serializer = LessonDetailSerializer(lessons, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, course_id, module_id):
        # Check teacher is verified
        teacher_profile = TeacherProfile.objects.filter(user=request.user).first()
        if not teacher_profile or teacher_profile.verification_status != 'approved':
            return Response(
                {'error': 'Your teacher profile must be approved to create lessons.'},
                status=status.HTTP_403_FORBIDDEN
            )

        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        module = get_object_or_404(course.modules, id=module_id)

        serializer = LessonCreateSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            lesson_type = serializer.validated_data['lesson_type']

            with transaction.atomic():
                # Extract video duration for video lessons
                duration = serializer.validated_data.get('duration')
                video_file = None
                
                if lesson_type == 'video':
                    video_file = serializer.validated_data.get('video_file')
                    if video_file:
                        # Rename video file to UUID-based filename for security
                        video_file.name = _generate_uuid_filename(video_file.name)
                        
                        extracted_duration = self._extract_video_duration(video_file)
                        if extracted_duration:
                            duration = extracted_duration

                # Create lesson
                lesson = Lesson.objects.create(
                    title=serializer.validated_data['title'],
                    lesson_type=lesson_type,
                    duration=duration
                )

                module.lessons.add(lesson)

                # Create type-specific lesson
                if lesson_type == 'video':
                    VideoLesson.objects.create(
                        lesson=lesson,
                        video_file=video_file,
                        transcript=serializer.validated_data.get('transcript', '')
                    )
                else:  # blog
                    BlogLesson.objects.create(
                        lesson=lesson,
                        content=serializer.validated_data.get('content', ''),
                        images=serializer.validated_data.get('images')
                    )

            message = self._handle_course_content_change(course)

            return Response(
                {
                    'message': message,
                    'lesson': LessonDetailSerializer(lesson, context={'request': request}).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _extract_video_duration(self, video_file):
        """Extract video duration in minutes using moviepy"""
        try:
            from moviepy.editor import VideoFileClip

            temp_path = None
            video_path = None

            try:
                if hasattr(video_file, 'temporary_file_path'):
                    video_path = video_file.temporary_file_path()
                else:
                    suffix = Path(getattr(video_file, 'name', '')).suffix or '.mp4'
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        for chunk in video_file.chunks():
                            tmp.write(chunk)
                        temp_path = tmp.name
                    video_path = temp_path
                    if hasattr(video_file, 'seek'):
                        video_file.seek(0)

                with VideoFileClip(video_path) as clip:
                    duration_seconds = clip.duration

                if duration_seconds:
                    return max(1, math.ceil(duration_seconds / 60))
            finally:
                if temp_path:
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass
        except Exception:
            pass

        return None

    def _handle_course_content_change(self, course):
        if course.is_published:
            course.is_published = False
            course.is_submitted_for_review = True
            course.admin_approved = False
            course.save()
            return "Lesson added. Course unpublished and resubmitted for review."
        return "Lesson added successfully."


class LessonDetailAPIView(RetrieveAPIView):
    """
    GET /api/v1/teacher/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/
    Returns lesson details
    """
    permission_classes = [IsTeacher, IsOnboardingComplete, IsLessonOwner]
    serializer_class = LessonDetailSerializer
    lookup_url_kwarg = 'lesson_id'

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        module_id = self.kwargs.get('module_id')
        course = get_object_or_404(Course, id=course_id, published_by=self.request.user)
        module = get_object_or_404(course.modules, id=module_id)
        return module.lessons.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class LessonUpdateView(APIView):
    """
    PUT/PATCH /api/v1/teacher/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/
    Update lesson information
    """
    permission_classes = [IsTeacher, IsTeacherVerified, IsOnboardingComplete, IsLessonOwner]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def put(self, request, course_id, module_id, lesson_id):
        return self._update(request, course_id, module_id, lesson_id, partial=False)

    def patch(self, request, course_id, module_id, lesson_id):
        return self._update(request, course_id, module_id, lesson_id, partial=True)

    def _update(self, request, course_id, module_id, lesson_id, partial):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        module = get_object_or_404(course.modules, id=module_id)
        lesson = get_object_or_404(module.lessons, id=lesson_id)

        serializer = LessonUpdateSerializer(lesson, data=request.data, partial=partial, context={'request': request})

        if serializer.is_valid():
            with transaction.atomic():
                # Update lesson
                lesson.title = serializer.validated_data.get('title', lesson.title)
                lesson.lesson_type = serializer.validated_data.get('lesson_type', lesson.lesson_type)

                # Handle duration
                if 'duration' in serializer.validated_data:
                    lesson.duration = serializer.validated_data['duration']

                lesson.save()

                # Update type-specific content
                if lesson.lesson_type == 'video':
                    video_lesson, _ = VideoLesson.objects.get_or_create(lesson=lesson)
                    if 'video_file' in serializer.validated_data:
                        video_file = serializer.validated_data['video_file']
                        # Rename video file to UUID-based filename for security
                        video_file.name = _generate_uuid_filename(video_file.name)
                        video_lesson.video_file = video_file
                    if 'transcript' in serializer.validated_data:
                        video_lesson.transcript = serializer.validated_data['transcript']
                    video_lesson.save()
                else:  # blog
                    blog_lesson, _ = BlogLesson.objects.get_or_create(lesson=lesson)
                    if 'content' in serializer.validated_data:
                        blog_lesson.content = serializer.validated_data['content']
                    if 'images' in serializer.validated_data:
                        blog_lesson.images = serializer.validated_data['images']
                    blog_lesson.save()

            message = self._handle_course_content_change(course)

            return Response(
                {
                    'message': message,
                    'lesson': LessonDetailSerializer(lesson, context={'request': request}).data
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _handle_course_content_change(self, course):
        if course.is_published:
            course.is_published = False
            course.is_submitted_for_review = True
            course.admin_approved = False
            course.save()
            return "Changes saved. Course unpublished and resubmitted for review."
        return "Changes saved successfully."


class LessonDeleteView(APIView):
    """
    DELETE /api/v1/teacher/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/
    Delete a lesson
    """
    permission_classes = [IsTeacher, IsTeacherVerified, IsOnboardingComplete, IsLessonOwner]

    def delete(self, request, course_id, module_id, lesson_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        module = get_object_or_404(course.modules, id=module_id)
        lesson = get_object_or_404(module.lessons, id=lesson_id)

        module.lessons.remove(lesson)
        lesson.delete()

        message = self._handle_course_content_change(course)

        return Response(
            {'message': message},
            status=status.HTTP_204_NO_CONTENT
        )

    def _handle_course_content_change(self, course):
        if course.is_published:
            course.is_published = False
            course.is_submitted_for_review = True
            course.admin_approved = False
            course.save()
            return "Lesson deleted. Course unpublished and resubmitted for review."
        return "Lesson deleted successfully."


# ===== Preview & Analytics =====

class CoursePreviewView(RetrieveAPIView):
    """
    GET /api/v1/teacher/courses/{course_id}/preview/
    Returns full course structure for preview
    """
    permission_classes = [IsTeacher, IsOnboardingComplete, IsCourseOwner]
    serializer_class = TeacherCourseDetailSerializer
    lookup_url_kwarg = 'course_id'

    def get_queryset(self):
        return Course.objects.filter(
            published_by=self.request.user
        ).prefetch_related('modules', 'modules__lessons', 'modules__lessons__video', 'modules__lessons__blog')


class LessonPreviewView(APIView):
    """
    GET /api/v1/teacher/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/preview/
    Returns lesson preview data
    Accessible by course owner (teacher) or admins for course review
    """
    permission_classes = [IsOnboardingComplete]

    def get(self, request, course_id, module_id, lesson_id):
        # Import here to avoid circular import
        from teacher_dash.permissions import IsLessonOwnerOrAdmin
        
        # Check permission manually
        permission = IsLessonOwnerOrAdmin()
        if not permission.has_permission(request, self):
            return Response(
                {'error': 'You do not have permission to preview this lesson.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Admins can access any course, teachers only their own
        user_role = getattr(request.user, 'role', None)
        if user_role == 'admin':
            course = get_object_or_404(Course, id=course_id)
        else:
            course = get_object_or_404(Course, id=course_id, published_by=request.user)
        
        module = get_object_or_404(course.modules, id=module_id)
        lesson = get_object_or_404(module.lessons, id=lesson_id)

        serializer = LessonDetailSerializer(lesson, context={'request': request})
        return Response(serializer.data)


class CourseAnalyticsView(APIView):
    """
    GET /api/v1/teacher/courses/{course_id}/analytics/
    Returns course analytics
    """
    permission_classes = [IsTeacher, IsOnboardingComplete, IsCourseOwner]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)

        # Get all lessons in course
        course_lessons = Lesson.objects.filter(module__course=course)
        completed_count = CompletedLesson.objects.filter(lesson__in=course_lessons).count()

        data = {
            'course': course,
            'enrollments': course.num_enrollments,
            'completed_lessons': completed_count,
        }

        serializer = CourseAnalyticsSerializer(data)
        return Response(serializer.data)


# ===== Publishing =====

class CoursePublishView(APIView):
    """
    POST /api/v1/teacher/courses/{course_id}/publish/
    Publish course or submit for review
    """
    permission_classes = [IsTeacher, IsTeacherVerified, IsOnboardingComplete, IsCourseOwner]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        profile = TeacherProfile.objects.filter(user=request.user).first()

        if profile and profile.verification_status == 'approved':
            if course.admin_approved:
                # Admin has approved, teacher can now publish
                course.is_published = True
                course.is_submitted_for_review = False
                course.save(update_fields=['is_published', 'is_submitted_for_review'])
                message = "Course published and now visible to students."
            else:
                # Submit for review
                if not course.is_submitted_for_review:
                    course.is_submitted_for_review = True
                    course.admin_review_feedback = ""
                    course.save(update_fields=['is_submitted_for_review', 'admin_review_feedback'])
                    self._notify_admins_course_submitted(course)
                    message = "Course submitted for admin review. You can publish after approval."
                else:
                    message = "Awaiting admin review. You'll be able to publish after approval."
        else:
            return Response(
                {'error': 'Your teacher profile must be approved to publish courses.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(
            {
                'message': message,
                'course': TeacherCourseDetailSerializer(course).data
            },
            status=status.HTTP_200_OK
        )

    def _notify_admins_course_submitted(self, course):
        try:
            mail_admins(
                subject="Course submitted for review",
                message=f"Course '{course.title}' requires approval.",
            )
        except Exception:
            pass


class CourseUnpublishView(APIView):
    """
    POST /api/v1/teacher/courses/{course_id}/unpublish/
    Unpublish a course
    """
    permission_classes = [IsTeacher, IsOnboardingComplete, IsCourseOwner]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        course.is_published = False
        course.save(update_fields=['is_published'])

        return Response(
            {
                'message': 'Course unpublished successfully.',
                'course': TeacherCourseDetailSerializer(course).data
            },
            status=status.HTTP_200_OK
        )


# ===== Export & Media =====

class ExportCoursesView(APIView):
    """
    GET /api/v1/teacher/courses/export/
    Export courses as CSV
    """
    permission_classes = [IsTeacher, IsOnboardingComplete]

    def get(self, request):
        courses = Course.objects.filter(published_by=request.user)

        lines = ["title,price,is_published,id"]
        for course in courses:
            lines.append(f"{course.title},{course.price},{course.is_published},{course.pk}")

        response = HttpResponse("\n".join(lines), content_type="text/csv")
        response['Content-Disposition'] = "attachment; filename=teacher_courses.csv"
        return response


def serve_video(request, video_path):
    """
    GET /api/v1/teacher/videos/{video_path}
    Serve video files with HTTP Range request support
    """
    import mimetypes

    # Build full file path
    file_path = os.path.join(settings.MEDIA_ROOT, video_path)

    # Security: Ensure file exists and is within MEDIA_ROOT
    real_media_root = os.path.realpath(settings.MEDIA_ROOT)
    real_file_path = os.path.realpath(file_path)

    if not os.path.exists(real_file_path) or not real_file_path.startswith(real_media_root):
        return HttpResponse("Video not found", status=404)

    # Get file size
    file_size = os.path.getsize(real_file_path)

    # Determine content type
    content_type, _ = mimetypes.guess_type(real_file_path)
    content_type = content_type or 'video/mp4'

    # Check for Range header
    range_header = request.META.get('HTTP_RANGE', '').strip()

    if range_header:
        # Parse range header
        range_match = range_header.replace('bytes=', '').split('-')
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if len(range_match) > 1 and range_match[1] else file_size - 1

        # Validate range
        if start >= file_size or end >= file_size or start > end:
            return HttpResponse("Invalid range", status=416)

        # Calculate content length
        length = end - start + 1

        # Open file and seek to start position
        file_handle = open(real_file_path, 'rb')
        file_handle.seek(start)

        # Create response with partial content
        response = FileResponse(file_handle, content_type=content_type, status=206)
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response['Content-Length'] = str(length)
        response['Accept-Ranges'] = 'bytes'

        return response
    else:
        # No range header - serve full file
        response = FileResponse(open(real_file_path, 'rb'), content_type=content_type)
        response['Content-Length'] = str(file_size)
        response['Accept-Ranges'] = 'bytes'

        return response


# ===== Discussions =====

class CourseDiscussionsView(ListAPIView):
    """
    GET /api/v1/teacher/courses/{course_id}/discussions/
    List course discussions for moderation
    """
    permission_classes = [IsTeacher, IsOnboardingComplete, IsCourseOwner]
    serializer_class = TeacherDiscussionPostSerializer

    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return DiscussionPost.objects.none()
        
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id, published_by=self.request.user)

        sort_param = self.request.query_params.get('sort', 'recent')

        queryset = DiscussionPost.objects.filter(
            course=course,
            parent_post__isnull=True
        ).select_related('user').prefetch_related('replies')

        if sort_param == 'pinned':
            queryset = queryset.order_by('-is_pinned', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset


class DiscussionCreateView(APIView):
    """
    POST /api/v1/teacher/courses/{course_id}/discussions/
    Create discussion post as teacher
    """
    permission_classes = [IsTeacher, IsOnboardingComplete, IsCourseOwner]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)

        serializer = DiscussionPostCreateSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(
                course=course,
                user=request.user,
                parent_post=None
            )

            return Response(
                {
                    'message': 'Discussion post created successfully!',
                    'post': TeacherDiscussionPostSerializer(post).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiscussionDetailView(RetrieveAPIView):
    """
    GET /api/v1/teacher/courses/{course_id}/discussions/{post_id}/
    View discussion with replies
    """
    permission_classes = [IsTeacher, IsOnboardingComplete, IsCourseOwner]
    serializer_class = TeacherDiscussionPostSerializer
    lookup_url_kwarg = 'post_id'

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id, published_by=self.request.user)
        return DiscussionPost.objects.filter(course=course).select_related('user').prefetch_related('replies__user')


class DiscussionReplyView(APIView):
    """
    POST /api/v1/teacher/courses/{course_id}/discussions/{post_id}/replies/
    Reply to discussion post
    """
    permission_classes = [IsTeacher, IsOnboardingComplete, IsCourseOwner]

    def post(self, request, course_id, post_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        parent_post = get_object_or_404(DiscussionPost, id=post_id, course=course)

        serializer = DiscussionPostCreateSerializer(data=request.data)
        if serializer.is_valid():
            reply = serializer.save(
                course=course,
                user=request.user,
                parent_post=parent_post
            )

            return Response(
                {
                    'message': 'Reply posted successfully!',
                    'reply': TeacherDiscussionPostSerializer(reply).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiscussionEditView(APIView):
    """
    PUT /api/v1/teacher/courses/{course_id}/discussions/{post_id}/
    Edit discussion post
    """
    permission_classes = [IsTeacher, IsOnboardingComplete, IsCourseOwner]

    def put(self, request, course_id, post_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        post = get_object_or_404(DiscussionPost, id=post_id, course=course)

        if not post.can_edit(request.user):
            return Response(
                {'error': "You don't have permission to edit this post."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = DiscussionPostCreateSerializer(post, data=request.data)
        if serializer.is_valid():
            edited_post = serializer.save()
            edited_post.is_edited = True
            edited_post.edited_at = timezone.now()
            edited_post.save()

            return Response(
                {
                    'message': 'Post updated successfully!',
                    'post': TeacherDiscussionPostSerializer(edited_post).data
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiscussionDeleteView(APIView):
    """
    DELETE /api/v1/teacher/courses/{course_id}/discussions/{post_id}/
    Delete discussion post (teacher moderation)
    """
    permission_classes = [IsTeacher, IsOnboardingComplete, IsCourseOwner]

    def delete(self, request, course_id, post_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        post = get_object_or_404(DiscussionPost, id=post_id, course=course)

        post.delete()

        return Response(
            {'message': 'Post deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )


class DiscussionPinToggleView(APIView):
    """
    POST /api/v1/teacher/courses/{course_id}/discussions/{post_id}/pin/
    Pin or unpin discussion post
    """
    permission_classes = [IsTeacher, IsOnboardingComplete, IsCourseOwner]

    def post(self, request, course_id, post_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        post = get_object_or_404(DiscussionPost, id=post_id, course=course, parent_post__isnull=True)

        post.is_pinned = not post.is_pinned
        post.save(update_fields=['is_pinned'])

        message = "Post has been pinned!" if post.is_pinned else "Post has been unpinned!"

        return Response(
            {
                'message': message,
                'post': TeacherDiscussionPostSerializer(post).data
            },
            status=status.HTTP_200_OK
        )
