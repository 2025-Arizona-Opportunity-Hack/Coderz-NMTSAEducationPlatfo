"""
Teacher Management API Views
Handles teacher dashboard, course/module/lesson CRUD, and analytics
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Avg, Q, Sum
from datetime import timedelta
from decimal import Decimal

from teacher_dash.models import Course, Module, Lesson, VideoLesson, BlogLesson
from authentication.models import Enrollment, TeacherProfile
from lms.models import CompletedLesson
from api.serializers.teacher import (
    TeacherDashboardStatsSerializer,
    SimpleCourseSerializer,
    CourseDetailSerializer,
    CourseCreateUpdateSerializer,
    ModuleListSerializer,
    ModuleDetailSerializer,
    ModuleCreateUpdateSerializer,
    LessonListSerializer,
    LessonCreateSerializer,
    LessonUpdateSerializer,
    CourseAnalyticsSerializer,
    TeacherVerificationSerializer
)


class IsTeacher(IsAuthenticated):
    """Permission class for teacher-only access"""
    def has_permission(self, request, view):
        return (super().has_permission(request, view) and 
                request.user.role == 'teacher')


class IsTeacherOfCourse(IsTeacher):
    """Permission class for course owner"""
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Course):
            return obj.published_by == request.user
        return False


class TeacherDashboardView(APIView):
    """
    Get teacher dashboard statistics
    
    GET /api/teacher/dashboard
    """
    permission_classes = [IsTeacher]
    
    def get(self, request):
        teacher = request.user
        
        # Get all courses by teacher
        courses = Course.objects.filter(published_by=teacher)
        
        # Calculate stats
        total_courses = courses.count()
        published_courses = courses.filter(is_published=True).count()
        draft_courses = total_courses - published_courses
        
        # Total students (unique enrollments)
        total_students = Enrollment.objects.filter(
            course__in=courses,
            is_active=True
        ).values('user').distinct().count()
        
        # Total revenue
        total_revenue = Enrollment.objects.filter(
            course__in=courses,
            is_active=True,
            course__is_paid=True
        ).aggregate(
            total=Sum('course__price')
        )['total'] or Decimal('0.00')
        
        # Verification status
        try:
            teacher_profile = TeacherProfile.objects.get(user=teacher)
            verification_status = teacher_profile.verification_status
            is_verified = teacher_profile.is_verified
        except TeacherProfile.DoesNotExist:
            verification_status = 'pending'
            is_verified = False
        
        # Recent enrollments
        recent_enrollments = []
        recent_enroll_objs = Enrollment.objects.filter(
            course__in=courses,
            is_active=True
        ).select_related('user', 'course').order_by('-enrolled_at')[:5]
        
        for enrollment in recent_enroll_objs:
            recent_enrollments.append({
                'id': enrollment.id,
                'student_name': enrollment.user.get_full_name() or enrollment.user.username,
                'course_title': enrollment.course.title,
                'enrolled_at': enrollment.enrolled_at.isoformat(),
                'progress': enrollment.progress_percentage
            })
        
        # Prepare response
        data = {
            'total_courses': total_courses,
            'published_courses': published_courses,
            'draft_courses': draft_courses,
            'total_students': total_students,
            'total_revenue': str(total_revenue),
            'verification_status': verification_status,
            'is_verified': is_verified,
            'recent_enrollments': recent_enrollments
        }
        
        return Response({'data': data}, status=status.HTTP_200_OK)


class TeacherCoursesView(APIView):
    """
    List teacher's courses
    
    GET /api/teacher/courses?page=1&limit=10&status=all
    """
    permission_classes = [IsTeacher]
    
    def get(self, request):
        teacher = request.user
        
        # Get query params
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        status_filter = request.GET.get('status', 'all')
        
        # Base queryset
        queryset = Course.objects.filter(published_by=teacher)
        
        # Apply status filter
        if status_filter == 'published':
            queryset = queryset.filter(is_published=True)
        elif status_filter == 'draft':
            queryset = queryset.filter(is_published=False, is_submitted_for_review=False)
        elif status_filter == 'under_review':
            queryset = queryset.filter(is_submitted_for_review=True, is_published=False)
        
        # Order by
        queryset = queryset.order_by('-published_date', '-id')
        
        # Paginate
        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        courses = queryset[start:end]
        
        # Serialize
        serializer = SimpleCourseSerializer(courses, many=True)
        
        return Response({
            'data': serializer.data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'totalPages': (total + limit - 1) // limit
            }
        }, status=status.HTTP_200_OK)


class CourseCreateView(APIView):
    """
    Create new course
    
    POST /api/teacher/courses
    """
    permission_classes = [IsTeacher]
    
    def post(self, request):
        serializer = CourseCreateUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'message': 'Invalid data', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create course
        course = serializer.save(published_by=request.user)
        
        # Return created course
        response_serializer = SimpleCourseSerializer(course)
        return Response({
            'message': 'Course created successfully',
            'data': response_serializer.data
        }, status=status.HTTP_201_CREATED)


class CourseDetailUpdateDeleteView(APIView):
    """
    Get, update, or delete a course
    
    GET /api/teacher/courses/{id}
    PUT /api/teacher/courses/{id}
    DELETE /api/teacher/courses/{id}
    """
    permission_classes = [IsTeacher]
    
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        serializer = CourseDetailSerializer(course)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    
    def put(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        
        # Cannot edit published courses
        if course.is_published:
            return Response(
                {'message': 'Cannot edit published courses. Please unpublish first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CourseCreateUpdateSerializer(course, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response(
                {'message': 'Invalid data', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        
        response_serializer = CourseDetailSerializer(course)
        return Response({
            'message': 'Course updated successfully',
            'data': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        
        # Cannot delete published courses
        if course.is_published:
            return Response(
                {'message': 'Cannot delete published courses. Please unpublish first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        course.delete()
        return Response(
            {'message': 'Course deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


class CoursePublishView(APIView):
    """
    Publish/unpublish course
    
    POST /api/teacher/courses/{id}/publish
    POST /api/teacher/courses/{id}/unpublish
    """
    permission_classes = [IsTeacher]
    
    def post(self, request, course_id, action):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        
        # Check if teacher is verified
        try:
            teacher_profile = TeacherProfile.objects.get(user=request.user)
            if not teacher_profile.is_verified:
                return Response(
                    {'message': 'You must be verified to publish courses'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except TeacherProfile.DoesNotExist:
            return Response(
                {'message': 'Please complete teacher onboarding first'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if action == 'publish':
            # Validate course has content
            if course.modules.count() == 0:
                return Response(
                    {'message': 'Course must have at least one module'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            has_lessons = False
            for module in course.modules.all():
                if module.lessons.count() > 0:
                    has_lessons = True
                    break
            
            if not has_lessons:
                return Response(
                    {'message': 'Course must have at least one lesson'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            course.is_published = True
            course.published_date = timezone.now()
            course.save(update_fields=['is_published', 'published_date'])
            
            return Response(
                {'message': 'Course published successfully'},
                status=status.HTTP_200_OK
            )
        
        elif action == 'unpublish':
            course.is_published = False
            course.save(update_fields=['is_published'])
            
            return Response(
                {'message': 'Course unpublished successfully'},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'message': 'Invalid action'},
            status=status.HTTP_400_BAD_REQUEST
        )


class CourseModulesView(APIView):
    """
    List modules for a course
    
    GET /api/teacher/courses/{id}/modules
    """
    permission_classes = [IsTeacher]
    
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        modules = course.modules.order_by('order')
        serializer = ModuleListSerializer(modules, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class ModuleCreateView(APIView):
    """
    Create new module
    
    POST /api/teacher/courses/{id}/modules
    """
    permission_classes = [IsTeacher]
    
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        
        # Cannot edit published courses
        if course.is_published:
            return Response(
                {'message': 'Cannot edit published courses'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ModuleCreateUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'message': 'Invalid data', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create module
        module = serializer.save(course=course)
        
        response_serializer = ModuleListSerializer(module)
        return Response({
            'message': 'Module created successfully',
            'data': response_serializer.data
        }, status=status.HTTP_201_CREATED)


class ModuleDetailUpdateDeleteView(APIView):
    """
    Get, update, or delete a module
    
    GET /api/teacher/modules/{id}
    PUT /api/teacher/modules/{id}
    DELETE /api/teacher/modules/{id}
    """
    permission_classes = [IsTeacher]
    
    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__published_by=request.user)
        serializer = ModuleDetailSerializer(module)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    
    def put(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__published_by=request.user)
        
        # Cannot edit published courses
        if module.course.is_published:
            return Response(
                {'message': 'Cannot edit published courses'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ModuleCreateUpdateSerializer(module, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response(
                {'message': 'Invalid data', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        
        response_serializer = ModuleDetailSerializer(module)
        return Response({
            'message': 'Module updated successfully',
            'data': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__published_by=request.user)
        
        # Cannot edit published courses
        if module.course.is_published:
            return Response(
                {'message': 'Cannot delete modules from published courses'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        module.delete()
        return Response(
            {'message': 'Module deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


class ModuleLessonsView(APIView):
    """
    List lessons for a module
    
    GET /api/teacher/modules/{id}/lessons
    """
    permission_classes = [IsTeacher]
    
    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__published_by=request.user)
        lessons = module.lessons.order_by('order')
        serializer = LessonListSerializer(lessons, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class LessonCreateView(APIView):
    """
    Create new lesson
    
    POST /api/teacher/modules/{id}/lessons
    """
    permission_classes = [IsTeacher]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__published_by=request.user)
        
        # Cannot edit published courses
        if module.course.is_published:
            return Response(
                {'message': 'Cannot edit published courses'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = LessonCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'message': 'Invalid data', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create lesson
        lesson = serializer.save(module=module)
        
        response_serializer = LessonListSerializer(lesson)
        return Response({
            'message': 'Lesson created successfully',
            'data': response_serializer.data
        }, status=status.HTTP_201_CREATED)


class LessonDetailUpdateDeleteView(APIView):
    """
    Get, update, or delete a lesson
    
    GET /api/teacher/lessons/{id}
    PUT /api/teacher/lessons/{id}
    DELETE /api/teacher/lessons/{id}
    """
    permission_classes = [IsTeacher]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get(self, request, lesson_id):
        lesson = get_object_or_404(
            Lesson,
            id=lesson_id,
            module__course__published_by=request.user
        )
        serializer = LessonListSerializer(lesson)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    
    def put(self, request, lesson_id):
        lesson = get_object_or_404(
            Lesson,
            id=lesson_id,
            module__course__published_by=request.user
        )
        
        # Cannot edit published courses
        if lesson.module.course.is_published:
            return Response(
                {'message': 'Cannot edit published courses'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = LessonUpdateSerializer(lesson, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response(
                {'message': 'Invalid data', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        
        response_serializer = LessonListSerializer(lesson)
        return Response({
            'message': 'Lesson updated successfully',
            'data': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, lesson_id):
        lesson = get_object_or_404(
            Lesson,
            id=lesson_id,
            module__course__published_by=request.user
        )
        
        # Cannot edit published courses
        if lesson.module.course.is_published:
            return Response(
                {'message': 'Cannot delete lessons from published courses'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lesson.delete()
        return Response(
            {'message': 'Lesson deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


class CourseAnalyticsView(APIView):
    """
    Get course analytics
    
    GET /api/teacher/courses/{id}/analytics
    """
    permission_classes = [IsTeacher]
    
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, published_by=request.user)
        
        # Get enrollments
        enrollments = Enrollment.objects.filter(course=course, is_active=True)
        total_enrollments = enrollments.count()
        
        # Calculate average progress
        avg_progress = enrollments.aggregate(avg=Avg('progress_percentage'))['avg'] or 0
        
        # Completion rate
        completed_enrollments = enrollments.filter(progress_percentage=100).count()
        completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
        
        # Get ratings (assuming ratings exist on course)
        total_ratings = 0
        average_rating = 0.0
        rating_distribution = {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0}
        
        # Revenue
        revenue = 0
        if course.is_paid:
            revenue = total_enrollments * float(course.price)
        
        # Engagement metrics
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_enrollments = enrollments.filter(enrolled_at__gte=thirty_days_ago).count()
        
        # Most active students (by completed lessons)
        most_active = []
        for enrollment in enrollments[:10]:
            completed = CompletedLesson.objects.filter(
                user=enrollment.user,
                lesson__module__course=course
            ).count()
            
            most_active.append({
                'name': enrollment.user.get_full_name() or enrollment.user.username,
                'progress': enrollment.progress_percentage,
                'completed_lessons': completed,
                'enrolled_at': enrollment.enrolled_at.isoformat()
            })
        
        # Sort by completed lessons
        most_active.sort(key=lambda x: x['completed_lessons'], reverse=True)
        most_active = most_active[:5]
        
        # Prepare response
        data = {
            'total_enrollments': total_enrollments,
            'completion_rate': round(completion_rate, 2),
            'average_progress': round(avg_progress, 2),
            'total_ratings': total_ratings,
            'average_rating': average_rating,
            'rating_distribution': rating_distribution,
            'revenue': revenue,
            'recent_enrollments': recent_enrollments,
            'most_active_students': most_active
        }
        
        return Response({'data': data}, status=status.HTTP_200_OK)


class VerificationStatusView(APIView):
    """
    Get teacher verification status
    
    GET /api/teacher/verification
    """
    permission_classes = [IsTeacher]
    
    def get(self, request):
        try:
            teacher_profile = TeacherProfile.objects.get(user=request.user)
            serializer = TeacherVerificationSerializer(teacher_profile)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        except TeacherProfile.DoesNotExist:
            return Response(
                {'message': 'Teacher profile not found. Please complete onboarding.'},
                status=status.HTTP_404_NOT_FOUND
            )

