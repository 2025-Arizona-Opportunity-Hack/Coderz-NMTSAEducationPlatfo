"""
API views for student dashboard
Handles courses, learning, discussions, and certificates
"""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, F
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination

from authentication.models import Enrollment
from authentication.permissions import IsStudent, IsOnboardingComplete
from teacher_dash.models import Course, Module, Lesson, DiscussionPost
from lms.models import CompletedLesson, VideoProgress
from student_dash.permissions import IsEnrolledInCourse, CanAccessDiscussion, IsDiscussionAuthor
from .serializers import (
    DashboardStatsSerializer,
    CourseListSerializer,
    EnrollmentSerializer,
    CourseDetailSerializer,
    LessonDetailSerializer,
    VideoProgressSerializer,
    SaveVideoProgressSerializer,
    CompletedLessonSerializer,
    CertificateSerializer,
    DiscussionPostSerializer,
    DiscussionPostCreateSerializer,
    DiscussionReplyCreateSerializer,
)


# ===== Dashboard & Courses =====

class StudentDashboardView(APIView):
    """
    GET /api/v1/student/dashboard/
    Returns student dashboard with statistics and course information
    """
    permission_classes = [IsStudent, IsOnboardingComplete]

    def get(self, request):
        user = request.user

        # Get enrolled courses
        enrollments = Enrollment.objects.filter(
            user=user,
            is_active=True
        ).select_related('course', 'course__published_by')

        # Statistics
        enrolled_count = enrollments.count()
        completed_count = enrollments.filter(completed_at__isnull=False).count()

        # Calculate learning hours (simplified)
        learning_hours = sum([e.progress_percentage * 0.1 for e in enrollments])

        # In-progress courses
        in_progress_courses = enrollments.filter(
            completed_at__isnull=True,
            progress_percentage__lt=100
        ).order_by('-enrolled_at')[:3]

        # Recommended courses (not enrolled)
        enrolled_course_ids = enrollments.values_list('course_id', flat=True)
        recommended_courses = Course.objects.filter(
            is_published=True
        ).exclude(
            id__in=enrolled_course_ids
        ).order_by('-num_enrollments')[:6]

        data = {
            'enrolled_count': enrolled_count,
            'completed_count': completed_count,
            'learning_hours': int(learning_hours),
            'in_progress_courses': in_progress_courses,
            'recommended_courses': recommended_courses,
        }

        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)


class EnrolledCoursesView(ListAPIView):
    """
    GET /api/v1/student/courses/
    Returns paginated list of enrolled courses
    """
    permission_classes = [IsStudent, IsOnboardingComplete]
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        return Enrollment.objects.filter(
            user=self.request.user,
            is_active=True
        ).select_related('course', 'course__published_by').order_by('-enrolled_at')


class CourseCatalogView(ListAPIView):
    """
    GET /api/v1/student/catalog/
    Returns paginated, filtered list of published courses
    Query params: q, price_min, price_max, tag, sort
    No authentication required - public course browsing
    """
    permission_classes = []  # Public access
    serializer_class = CourseListSerializer

    def get_queryset(self):
        qs = Course.objects.filter(is_published=True).select_related('published_by').prefetch_related('tags')

        # Filters
        q = self.request.query_params.get('q', '').strip()
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        tag = self.request.query_params.get('tag', '').strip()
        sort = self.request.query_params.get('sort', 'newest')

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        if price_min:
            try:
                qs = qs.filter(price__gte=float(price_min))
            except ValueError:
                pass

        if price_max:
            try:
                qs = qs.filter(price__lte=float(price_max))
            except ValueError:
                pass

        if tag:
            qs = qs.filter(tags__name__iexact=tag)

        # Sorting
        if sort == 'popular':
            qs = qs.order_by('-num_enrollments', '-published_date')
        elif sort == 'price_asc':
            qs = qs.order_by('price')
        elif sort == 'price_desc':
            qs = qs.order_by('-price')
        else:  # newest
            qs = qs.order_by('-published_date')

        return qs


class CourseDetailView(RetrieveAPIView):
    """
    GET /api/v1/student/courses/{course_id}/
    Returns full course details with modules and lessons
    No authentication required - public course viewing
    """
    permission_classes = []  # Public access
    serializer_class = CourseDetailSerializer
    queryset = Course.objects.filter(is_published=True).prefetch_related('modules', 'modules__lessons')
    lookup_url_kwarg = 'course_id'


class CourseCategoriesView(APIView):
    """
    GET /api/v1/student/courses/categories
    Returns all unique tags from published courses as categories
    No authentication required - public access
    """
    permission_classes = []  # Public access

    def get(self, request):
        # Get all unique tags from published courses
        from taggit.models import Tag
        tags = Tag.objects.filter(
            taggit_taggeditem_items__content_type__model='course',
            taggit_taggeditem_items__object_id__in=Course.objects.filter(is_published=True).values_list('id', flat=True)
        ).distinct().values_list('name', flat=True)
        
        return Response({'data': list(tags)})


# ===== Enrollment =====

class EnrollInCourseView(APIView):
    """
    POST /api/v1/student/courses/{course_id}/enroll/
    Enroll student in a free course
    """
    permission_classes = [IsStudent, IsOnboardingComplete]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, is_published=True)
        user = request.user

        # Check if course is paid
        if course.is_paid:
            return Response(
                {'error': 'This is a paid course. Please use the checkout endpoint.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if already enrolled
        existing_enrollment = Enrollment.objects.filter(user=user, course=course).first()
        if existing_enrollment:
            return Response(
                {'error': "You're already enrolled in this course!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create enrollment
        with transaction.atomic():
            enrollment = Enrollment.objects.create(
                user=user,
                course=course,
                progress_percentage=0,
                is_active=True
            )
            # Update course enrollment count
            Course.objects.filter(pk=course.pk).update(num_enrollments=F('num_enrollments') + 1)

        return Response(
            {
                'message': f"Successfully enrolled in {course.title}!",
                'enrollment': EnrollmentSerializer(enrollment).data
            },
            status=status.HTTP_201_CREATED
        )


class CheckoutView(RetrieveAPIView):
    """
    GET /api/v1/student/courses/{course_id}/checkout/
    Returns checkout information for a paid course
    """
    permission_classes = [IsStudent, IsOnboardingComplete]
    serializer_class = CourseDetailSerializer
    lookup_url_kwarg = 'course_id'

    def get_queryset(self):
        return Course.objects.filter(is_published=True, is_paid=True)

    def retrieve(self, request, *args, **kwargs):
        course = self.get_object()
        user = request.user

        # Check if already enrolled
        existing_enrollment = Enrollment.objects.filter(user=user, course=course).first()
        if existing_enrollment:
            return Response(
                {'error': "You're already enrolled in this course!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(course)
        return Response(serializer.data)


class ProcessCheckoutView(APIView):
    """
    POST /api/v1/student/courses/{course_id}/checkout/
    Process payment and create enrollment (simulated for now)
    """
    permission_classes = [IsStudent, IsOnboardingComplete]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, is_published=True)
        user = request.user

        # Check if already enrolled
        existing_enrollment = Enrollment.objects.filter(user=user, course=course).first()
        if existing_enrollment:
            return Response(
                {'error': "You're already enrolled in this course!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Simulate payment processing
        # In production, integrate with Stripe/PayPal here

        # Create enrollment
        with transaction.atomic():
            enrollment = Enrollment.objects.create(
                user=user,
                course=course,
                progress_percentage=0,
                is_active=True
            )
            Course.objects.filter(pk=course.pk).update(num_enrollments=F('num_enrollments') + 1)

        return Response(
            {
                'message': f"Payment successful! You're now enrolled in {course.title}. Welcome aboard!",
                'enrollment': EnrollmentSerializer(enrollment).data
            },
            status=status.HTTP_201_CREATED
        )


# ===== Learning =====

class LearningView(APIView):
    """
    GET /api/v1/student/courses/{course_id}/learn/
    Returns course structure and first lesson information
    """
    permission_classes = [IsStudent, IsOnboardingComplete, IsEnrolledInCourse]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

        # Get all modules with lessons
        modules = course.modules.all().prefetch_related('lessons')

        # Find first lesson
        first_lesson = None
        first_module = None
        for module in modules:
            if module.lessons.exists():
                first_module = module
                first_lesson = module.lessons.first()
                break

        if not first_lesson or not first_module:
            return Response(
                {'error': "This course doesn't have any lessons yet."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'course': CourseDetailSerializer(course, context={'request': request}).data,
            'enrollment': EnrollmentSerializer(enrollment).data,
            'first_lesson': {
                'course_id': course_id,
                'module_id': first_module.id,
                'lesson_id': first_lesson.id,
            }
        })


class LessonView(APIView):
    """
    GET /api/v1/student/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/
    Returns lesson content with navigation and progress
    """
    permission_classes = [IsStudent, IsOnboardingComplete, IsEnrolledInCourse]

    def get(self, request, course_id, module_id, lesson_id):
        course = get_object_or_404(Course, id=course_id)
        enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
        module = get_object_or_404(Module, id=module_id)
        current_lesson = get_object_or_404(Lesson, id=lesson_id)

        # Get all modules for navigation
        modules = course.modules.all().prefetch_related('lessons').order_by('id')

        # Get completed lesson IDs
        completed_lesson_ids = list(
            CompletedLesson.objects.filter(enrollment=enrollment).values_list('lesson_id', flat=True)
        )

        # Get video progress
        video_progress = None
        if current_lesson.lesson_type == 'video':
            video_progress = VideoProgress.objects.filter(
                enrollment=enrollment,
                lesson=current_lesson
            ).first()

        # Find all lessons for navigation
        all_lessons = []
        for mod in modules:
            for lesson in mod.lessons.all():
                lesson.module_id = mod.id
                all_lessons.append(lesson)

        # Find previous and next lessons
        current_index = next((i for i, l in enumerate(all_lessons) if l.id == lesson_id), None)
        previous_lesson = all_lessons[current_index - 1] if current_index and current_index > 0 else None
        next_lesson = all_lessons[current_index + 1] if current_index is not None and current_index < len(all_lessons) - 1 else None

        # Serialize lesson with context
        lesson_serializer = LessonDetailSerializer(
            current_lesson,
            context={
                'request': request,
                'enrollment': enrollment,
                'module_id': module_id
            }
        )

        return Response({
            'course': CourseDetailSerializer(course, context={'request': request}).data,
            'enrollment': EnrollmentSerializer(enrollment).data,
            'module': {'id': module.id, 'title': module.title},
            'lesson': lesson_serializer.data,
            'completed_lesson_ids': completed_lesson_ids,
            'previous_lesson': LessonDetailSerializer(
                previous_lesson,
                context={'request': request, 'enrollment': enrollment, 'module_id': previous_lesson.module_id if previous_lesson else None}
            ).data if previous_lesson else None,
            'next_lesson': LessonDetailSerializer(
                next_lesson,
                context={'request': request, 'enrollment': enrollment, 'module_id': next_lesson.module_id if next_lesson else None}
            ).data if next_lesson else None,
            'video_progress': VideoProgressSerializer(video_progress).data if video_progress else None,
        })


class MarkLessonCompleteView(APIView):
    """
    POST /api/v1/student/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/complete/
    Mark a lesson as complete and update progress
    """
    permission_classes = [IsStudent, IsOnboardingComplete, IsEnrolledInCourse]

    def post(self, request, course_id, module_id, lesson_id):
        course = get_object_or_404(Course, id=course_id)
        enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
        lesson = get_object_or_404(Lesson, id=lesson_id)

        with transaction.atomic():
            # Create CompletedLesson if not exists
            CompletedLesson.objects.get_or_create(enrollment=enrollment, lesson=lesson)

            # Recalculate progress
            modules = course.modules.all().prefetch_related('lessons')
            total_lessons = sum([m.lessons.count() for m in modules]) or 1

            completed_count = CompletedLesson.objects.filter(enrollment=enrollment).count()
            progress = int((completed_count / total_lessons) * 100)

            # Update enrollment
            Enrollment.objects.filter(pk=enrollment.pk).update(
                progress_percentage=progress,
                completed_at=timezone.now() if progress >= 100 and not enrollment.completed_at else enrollment.completed_at,
            )

            # Refresh enrollment
            enrollment.refresh_from_db()

        return Response(
            {
                'message': 'Lesson marked as complete!',
                'enrollment': EnrollmentSerializer(enrollment).data
            },
            status=status.HTTP_200_OK
        )


class SaveVideoProgressView(APIView):
    """
    POST /api/v1/student/video-progress/
    Save video playback progress
    Body: {lesson_id, current_time, duration}
    """
    permission_classes = [IsStudent, IsOnboardingComplete]

    def post(self, request):
        serializer = SaveVideoProgressSerializer(data=request.data)
        if serializer.is_valid():
            lesson_id = serializer.validated_data['lesson_id']
            current_time = serializer.validated_data['current_time']
            duration = serializer.validated_data['duration']

            lesson = get_object_or_404(Lesson, id=lesson_id)
            enrollment = get_object_or_404(
                Enrollment,
                user=request.user,
                course__modules__lessons=lesson
            )

            # Calculate completion percentage
            completed_percentage = 0
            if duration > 0:
                completed_percentage = min(int((current_time / duration) * 100), 100)

            # Update or create video progress
            video_progress, created = VideoProgress.objects.update_or_create(
                enrollment=enrollment,
                lesson=lesson,
                defaults={
                    'last_position_seconds': int(current_time),
                    'completed_percentage': completed_percentage
                }
            )

            return Response(
                {
                    'success': True,
                    'progress': completed_percentage,
                    'position': int(current_time)
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ===== Certificates =====

class CertificateView(APIView):
    """
    GET /api/v1/student/courses/{course_id}/certificate/
    Returns certificate data for completed course
    """
    permission_classes = [IsStudent, IsOnboardingComplete]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        enrollment = get_object_or_404(
            Enrollment,
            user=request.user,
            course=course,
            completed_at__isnull=False
        )

        data = {
            'course': course,
            'enrollment': enrollment,
            'student_name': request.user.get_full_name(),
            'completion_date': enrollment.completed_at,
            'certificate_id': f'CERT-{course.id}-{enrollment.id}',
        }

        serializer = CertificateSerializer(data)
        return Response(serializer.data)


class CertificatePDFView(APIView):
    """
    GET /api/v1/student/courses/{course_id}/certificate/pdf/
    Generate and return PDF certificate (or HTML for client-side generation)
    """
    permission_classes = [IsStudent, IsOnboardingComplete]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        enrollment = get_object_or_404(
            Enrollment,
            user=request.user,
            course=course,
            completed_at__isnull=False
        )

        # For now, return HTML that frontend can convert to PDF
        # In production, you could use WeasyPrint to generate PDF server-side
        html_string = render_to_string('student_dash/certificate.html', {
            'course': course,
            'enrollment': enrollment,
        }, request=request)

        return HttpResponse(html_string, content_type='text/html')


# ===== Discussions =====

class CourseDiscussionsView(ListAPIView):
    """
    GET /api/v1/student/courses/{course_id}/discussions/
    Returns paginated discussion posts
    Query params: sort (recent/unanswered/pinned), page
    """
    permission_classes = [IsStudent, IsOnboardingComplete, CanAccessDiscussion]
    serializer_class = DiscussionPostSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id, is_published=True)

        sort_param = self.request.query_params.get('sort', 'recent')

        # Top-level posts only
        queryset = DiscussionPost.objects.filter(
            course=course,
            parent_post__isnull=True
        ).select_related('user').prefetch_related('replies')

        # Apply sorting
        if sort_param == 'unanswered':
            from django.db.models import Count
            queryset = queryset.annotate(reply_count=Count('replies')).filter(reply_count=0).order_by('-created_at')
        elif sort_param == 'pinned':
            queryset = queryset.order_by('-is_pinned', '-created_at')
        else:  # recent
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        course_id = self.kwargs.get('course_id')
        context['course'] = get_object_or_404(Course, id=course_id)
        return context


class DiscussionCreateView(APIView):
    """
    POST /api/v1/student/courses/{course_id}/discussions/
    Create a new discussion post
    """
    permission_classes = [IsStudent, IsOnboardingComplete, CanAccessDiscussion]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, is_published=True)

        # Rate limiting check
        from datetime import timedelta
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_posts_count = DiscussionPost.objects.filter(
            course=course,
            user=request.user,
            created_at__gte=one_hour_ago
        ).count()

        if recent_posts_count >= 10:
            return Response(
                {'error': "You've reached the posting limit (10 posts per hour). Please wait before posting again."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        serializer = DiscussionPostCreateSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(
                course=course,
                user=request.user,
                parent_post=None
            )

            return Response(
                {
                    'message': 'Your discussion post has been created!',
                    'post': DiscussionPostSerializer(post, context={'request': request, 'course': course}).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiscussionDetailView(RetrieveAPIView):
    """
    GET /api/v1/student/courses/{course_id}/discussions/{post_id}/
    Returns discussion post with all replies
    """
    permission_classes = [IsStudent, IsOnboardingComplete, CanAccessDiscussion]
    serializer_class = DiscussionPostSerializer
    lookup_url_kwarg = 'post_id'

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id, is_published=True)
        return DiscussionPost.objects.filter(course=course).select_related('user').prefetch_related('replies__user')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        course_id = self.kwargs.get('course_id')
        context['course'] = get_object_or_404(Course, id=course_id)
        return context


class DiscussionReplyView(APIView):
    """
    POST /api/v1/student/courses/{course_id}/discussions/{post_id}/replies/
    Reply to a discussion post
    """
    permission_classes = [IsStudent, IsOnboardingComplete, CanAccessDiscussion]

    def post(self, request, course_id, post_id):
        course = get_object_or_404(Course, id=course_id, is_published=True)
        parent_post = get_object_or_404(DiscussionPost, id=post_id, course=course)

        # Rate limiting
        from datetime import timedelta
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_posts_count = DiscussionPost.objects.filter(
            course=course,
            user=request.user,
            created_at__gte=one_hour_ago
        ).count()

        if recent_posts_count >= 10:
            return Response(
                {'error': "You've reached the posting limit (10 posts per hour). Please wait before replying again."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        serializer = DiscussionReplyCreateSerializer(data=request.data)
        if serializer.is_valid():
            reply = serializer.save(
                course=course,
                user=request.user,
                parent_post=parent_post
            )

            return Response(
                {
                    'message': 'Your reply has been posted!',
                    'reply': DiscussionReplySerializer(reply, context={'request': request, 'course': course}).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiscussionEditView(APIView):
    """
    PUT /api/v1/student/courses/{course_id}/discussions/{post_id}/
    Edit a discussion post or reply
    """
    permission_classes = [IsStudent, IsOnboardingComplete, CanAccessDiscussion]

    def put(self, request, course_id, post_id):
        course = get_object_or_404(Course, id=course_id, is_published=True)
        post = get_object_or_404(DiscussionPost, id=post_id, course=course)

        # Check if user can edit
        if not post.can_edit(request.user):
            return Response(
                {'error': "You don't have permission to edit this post, or the editing time limit has expired."},
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
                    'message': 'Your post has been updated!',
                    'post': DiscussionPostSerializer(edited_post, context={'request': request, 'course': course}).data
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiscussionDeleteView(APIView):
    """
    DELETE /api/v1/student/courses/{course_id}/discussions/{post_id}/
    Delete a discussion post or reply
    """
    permission_classes = [IsStudent, IsOnboardingComplete, CanAccessDiscussion]

    def delete(self, request, course_id, post_id):
        course = get_object_or_404(Course, id=course_id, is_published=True)
        post = get_object_or_404(DiscussionPost, id=post_id, course=course)

        # Check if user can delete
        if not post.can_delete(request.user, course):
            return Response(
                {'error': "You don't have permission to delete this post."},
                status=status.HTTP_403_FORBIDDEN
            )

        post.delete()

        return Response(
            {'message': 'Post deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )
