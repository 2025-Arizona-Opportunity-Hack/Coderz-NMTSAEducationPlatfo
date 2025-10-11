"""
Dashboard API Views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from authentication.models import Enrollment
from teacher_dash.models import Course
from lms.models import CompletedLesson
from api.serializers import EnrollmentWithProgressSerializer
from api.views.courses import StandardResultsSetPagination


class DashboardStatsView(APIView):
    """
    Get dashboard statistics for current user
    
    GET /api/dashboard/stats
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get enrollments
        enrollments = Enrollment.objects.filter(user=user, is_active=True)
        
        # Total courses enrolled
        total_courses = enrollments.count()
        
        # In progress courses (not completed)
        in_progress = enrollments.filter(
            completed_at__isnull=True,
            progress_percentage__lt=100
        ).count()
        
        # Completed courses
        completed = enrollments.filter(completed_at__isnull=False).count()
        
        # Total certificates (same as completed for now)
        total_certificates = completed
        
        # Calculate learning hours (rough estimate)
        # Sum of progress_percentage * estimated course duration
        learning_hours = 0
        for enrollment in enrollments:
            # Calculate total course duration
            course_duration = 0
            for module in enrollment.course.modules.all():
                for lesson in module.lessons.all():
                    if lesson.duration:
                        course_duration += lesson.duration
            
            # Multiply by progress percentage
            if course_duration > 0:
                learning_hours += (enrollment.progress_percentage / 100.0) * (course_duration / 60.0)
        
        # Calculate streak (placeholder implementation)
        current_streak = 0
        longest_streak = 0
        
        # TODO: Implement actual streak calculation based on daily activity
        
        stats = {
            'totalCourses': total_courses,
            'inProgressCourses': in_progress,
            'completedCourses': completed,
            'totalCertificates': total_certificates,
            'totalLearningHours': int(learning_hours),
            'currentStreak': current_streak,
            'longestStreak': longest_streak
        }
        
        return Response({'data': stats})


class DashboardEnrollmentsView(APIView):
    """
    Get user enrollments with progress
    
    GET /api/dashboard/enrollments?page=1&limit=10&status=in-progress
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get(self, request):
        user = request.user
        
        # Base queryset
        queryset = Enrollment.objects.filter(
            user=user,
            is_active=True
        ).select_related('course', 'course__published_by').order_by('-enrolled_at')
        
        # Filter by status
        status_filter = request.GET.get('status', '').strip()
        if status_filter == 'in-progress':
            queryset = queryset.filter(
                completed_at__isnull=True,
                progress_percentage__lt=100
            )
        elif status_filter == 'completed':
            queryset = queryset.filter(completed_at__isnull=False)
        
        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = EnrollmentWithProgressSerializer(
                page, 
                many=True, 
                context={'request': request}
            )
            return paginator.get_paginated_response(serializer.data)
        
        serializer = EnrollmentWithProgressSerializer(
            queryset, 
            many=True, 
            context={'request': request}
        )
        return Response({'data': serializer.data})


class ContinueLearningView(APIView):
    """
    Get continue learning recommendations
    
    GET /api/dashboard/continue-learning
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get in-progress enrollments
        enrollments = Enrollment.objects.filter(
            user=user,
            is_active=True,
            completed_at__isnull=True,
            progress_percentage__lt=100
        ).select_related('course', 'course__published_by').order_by(
            '-last_accessed_at', '-enrolled_at'
        )[:5]
        
        continue_learning_items = []
        
        for enrollment in enrollments:
            # Find next incomplete lesson
            completed_lesson_ids = set(
                CompletedLesson.objects.filter(enrollment=enrollment)
                .values_list('lesson_id', flat=True)
            )
            
            next_lesson = None
            for module in enrollment.course.modules.all().order_by('id'):
                for lesson in module.lessons.all().order_by('id'):
                    if lesson.id not in completed_lesson_ids:
                        next_lesson = {
                            'id': str(lesson.id),
                            'title': lesson.title,
                            'type': lesson.lesson_type,
                            'duration': lesson.duration or 0
                        }
                        break
                if next_lesson:
                    break
            
            if next_lesson:
                continue_learning_items.append({
                    'enrollment': EnrollmentWithProgressSerializer(
                        enrollment,
                        context={'request': request}
                    ).data,
                    'nextLesson': next_lesson
                })
        
        return Response({'data': continue_learning_items})


class CertificatesView(APIView):
    """
    Get user certificates
    
    GET /api/dashboard/certificates
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get completed enrollments
        completed_enrollments = Enrollment.objects.filter(
            user=user,
            completed_at__isnull=False
        ).select_related('course', 'course__published_by')
        
        certificates = []
        for enrollment in completed_enrollments:
            certificates.append({
                'id': str(enrollment.id),
                'courseId': str(enrollment.course_id),
                'userId': str(user.id),
                'course': {
                    'id': str(enrollment.course_id),
                    'title': enrollment.course.title,
                    'instructor': enrollment.course.published_by.get_full_name() or enrollment.course.published_by.username
                },
                'completedAt': enrollment.completed_at.isoformat() if enrollment.completed_at else None,
                'certificateUrl': f'/student/courses/{enrollment.course_id}/certificate/'
            })
        
        return Response({'data': certificates})
