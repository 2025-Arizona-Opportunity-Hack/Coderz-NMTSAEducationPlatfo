"""
Lesson Content and Progress API Views
Handles lesson viewing, completion tracking, and video progress
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count

from teacher_dash.models import Lesson, Course, Module
from authentication.models import Enrollment
from lms.models import CompletedLesson, VideoProgress
from api.serializers.lessons import (
    LessonContentSerializer,
    LessonCompletionSerializer,
    VideoProgressUpdateSerializer,
    CertificateSerializer
)


class LessonContentView(APIView):
    """
    Get lesson content with video/blog data and navigation
    
    GET /api/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_id, module_id, lesson_id):
        # Verify course exists and is published
        course = get_object_or_404(Course, id=course_id, is_published=True)
        
        # Verify module belongs to course
        module = get_object_or_404(Module, id=module_id)
        if not course.modules.filter(id=module_id).exists():
            return Response(
                {'message': 'Module does not belong to this course'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify lesson belongs to module
        lesson = get_object_or_404(Lesson, id=lesson_id)
        if not module.lessons.filter(id=lesson_id).exists():
            return Response(
                {'message': 'Lesson does not belong to this module'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is enrolled
        try:
            enrollment = Enrollment.objects.get(
                user=request.user,
                course=course,
                is_active=True
            )
            # Update last accessed
            enrollment.last_accessed_at = timezone.now()
            enrollment.current_lesson = lesson
            enrollment.save(update_fields=['last_accessed_at', 'current_lesson'])
        except Enrollment.DoesNotExist:
            return Response(
                {'message': 'You must be enrolled in this course to view lessons'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Serialize lesson with context
        serializer = LessonContentSerializer(
            lesson,
            context={
                'request': request,
                'course_id': course_id
            }
        )
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarkLessonCompleteView(APIView):
    """
    Mark a lesson as completed
    
    POST /api/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/complete
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, course_id, module_id, lesson_id):
        # Verify course, module, lesson
        course = get_object_or_404(Course, id=course_id, is_published=True)
        module = get_object_or_404(Module, id=module_id)
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        if not course.modules.filter(id=module_id).exists():
            return Response(
                {'message': 'Module does not belong to this course'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not module.lessons.filter(id=lesson_id).exists():
            return Response(
                {'message': 'Lesson does not belong to this module'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get enrollment
        try:
            enrollment = Enrollment.objects.get(
                user=request.user,
                course=course,
                is_active=True
            )
        except Enrollment.DoesNotExist:
            return Response(
                {'message': 'You must be enrolled in this course'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Mark lesson complete (get_or_create to avoid duplicates)
        completed_lesson, created = CompletedLesson.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
        
        # Calculate progress
        total_lessons = 0
        completed_lessons_count = 0
        
        for mod in course.modules.all():
            total_lessons += mod.lessons.count()
        
        completed_lessons_count = CompletedLesson.objects.filter(
            enrollment=enrollment
        ).count()
        
        # Update enrollment progress
        if total_lessons > 0:
            progress_percentage = int((completed_lessons_count / total_lessons) * 100)
            enrollment.progress_percentage = progress_percentage
            
            # Mark as completed if 100%
            if progress_percentage == 100 and not enrollment.completed_at:
                enrollment.completed_at = timezone.now()
            
            enrollment.save(update_fields=['progress_percentage', 'completed_at'])
        
        # Prepare response
        response_data = {
            'lesson_id': lesson.id,
            'course_id': course.id,
            'is_completed': True,
            'completed_at': completed_lesson.completed_at.isoformat(),
            'progress': {
                'completed_lessons': completed_lessons_count,
                'total_lessons': total_lessons,
                'percentage': enrollment.progress_percentage
            }
        }
        
        return Response(
            response_data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class UpdateVideoProgressView(APIView):
    """
    Update video playback progress
    
    PUT /api/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/video-progress
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request, course_id, module_id, lesson_id):
        # Validate input
        serializer = VideoProgressUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'message': 'Invalid data', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify course, module, lesson
        course = get_object_or_404(Course, id=course_id, is_published=True)
        module = get_object_or_404(Module, id=module_id)
        lesson = get_object_or_404(Lesson, id=lesson_id, lesson_type='video')
        
        if not course.modules.filter(id=module_id).exists():
            return Response(
                {'message': 'Module does not belong to this course'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not module.lessons.filter(id=lesson_id).exists():
            return Response(
                {'message': 'Lesson does not belong to this module'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get enrollment
        try:
            enrollment = Enrollment.objects.get(
                user=request.user,
                course=course,
                is_active=True
            )
        except Enrollment.DoesNotExist:
            return Response(
                {'message': 'You must be enrolled in this course'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update or create video progress
        video_progress, created = VideoProgress.objects.update_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={
                'last_position_seconds': serializer.validated_data['last_position_seconds'],
                'completed_percentage': serializer.validated_data['completed_percentage']
            }
        )
        
        return Response(
            {
                'message': 'Video progress updated successfully',
                'last_position_seconds': video_progress.last_position_seconds,
                'completed_percentage': video_progress.completed_percentage
            },
            status=status.HTTP_200_OK
        )


class CertificateView(APIView):
    """
    Get certificate for completed course
    
    GET /api/certificates/{enrollment_id}
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, enrollment_id):
        # Get enrollment
        enrollment = get_object_or_404(
            Enrollment,
            id=enrollment_id,
            user=request.user,
            is_active=True
        )
        
        # Check if course is completed
        if not enrollment.completed_at:
            return Response(
                {'message': 'Course not yet completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Serialize certificate data
        serializer = CertificateSerializer(enrollment, context={'request': request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class CertificatePDFView(APIView):
    """
    Download certificate PDF
    
    GET /api/certificates/{enrollment_id}/pdf
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, enrollment_id):
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from io import BytesIO
        
        # Get enrollment
        enrollment = get_object_or_404(
            Enrollment,
            id=enrollment_id,
            user=request.user,
            is_active=True
        )
        
        # Check if course is completed
        if not enrollment.completed_at:
            return Response(
                {'message': 'Course not yet completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=landscape(letter))
        width, height = landscape(letter)
        
        # Certificate border
        p.setStrokeColor(colors.HexColor('#1e3a8a'))
        p.setLineWidth(3)
        p.rect(0.5*inch, 0.5*inch, width-inch, height-inch)
        
        # Title
        p.setFont("Helvetica-Bold", 36)
        p.setFillColor(colors.HexColor('#1e3a8a'))
        p.drawCentredString(width/2, height-2*inch, "CERTIFICATE OF COMPLETION")
        
        # Subtitle
        p.setFont("Helvetica", 16)
        p.setFillColor(colors.black)
        p.drawCentredString(width/2, height-2.5*inch, "This is to certify that")
        
        # Student name
        p.setFont("Helvetica-Bold", 28)
        p.setFillColor(colors.HexColor('#1e3a8a'))
        student_name = request.user.get_full_name() or request.user.username
        p.drawCentredString(width/2, height-3.2*inch, student_name)
        
        # Course completion text
        p.setFont("Helvetica", 16)
        p.setFillColor(colors.black)
        p.drawCentredString(width/2, height-3.8*inch, "has successfully completed the course")
        
        # Course title
        p.setFont("Helvetica-Bold", 22)
        p.setFillColor(colors.HexColor('#1e3a8a'))
        p.drawCentredString(width/2, height-4.5*inch, enrollment.course.title)
        
        # Instructor
        p.setFont("Helvetica", 14)
        p.setFillColor(colors.black)
        instructor_name = enrollment.course.published_by.get_full_name() or enrollment.course.published_by.username
        p.drawCentredString(width/2, height-5.2*inch, f"Instructor: {instructor_name}")
        
        # Completion date
        completion_date = enrollment.completed_at.strftime("%B %d, %Y")
        p.drawCentredString(width/2, height-5.7*inch, f"Completed on: {completion_date}")
        
        # Certificate number
        p.setFont("Helvetica", 10)
        certificate_number = f"NMTSA-{enrollment.completed_at.year}-{enrollment.id:06d}"
        p.drawCentredString(width/2, 0.8*inch, f"Certificate No: {certificate_number}")
        
        # Credits (if applicable)
        if enrollment.course.credits > 0:
            p.drawCentredString(width/2, height-6.2*inch, f"Credits Earned: {enrollment.course.credits}")
        
        # Finalize PDF
        p.showPage()
        p.save()
        
        # Return PDF
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="certificate_{enrollment.id}.pdf"'
        
        return response
