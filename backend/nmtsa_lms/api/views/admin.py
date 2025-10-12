"""
Admin Management API Views
Handles admin dashboard, teacher verification, course review, user management
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta

from authentication.models import User, TeacherProfile, StudentProfile, Enrollment
from teacher_dash.models import Course
from api.serializers.admin import (
    AdminDashboardStatsSerializer,
    UserBasicSerializer,
    StudentDetailSerializer,
    TeacherDetailSerializer,
    TeacherVerificationSerializer,
    TeacherVerificationActionSerializer,
    CourseReviewSerializer,
    CourseReviewActionSerializer,
    UserManagementSerializer,
    UserUpdateSerializer,
    EnrollmentManagementSerializer,
    CourseManagementSerializer,
    CourseStatusUpdateSerializer
)


class IsAdmin(IsAuthenticated):
    """Permission class for admin-only access"""
    def has_permission(self, request, view):
        return (super().has_permission(request, view) and 
                request.user.role == 'admin')


class AdminDashboardView(APIView):
    """
    Get admin dashboard statistics
    
    GET /api/admin/dashboard
    """
    permission_classes = [IsAdmin]
    
    def get(self, request):
        # User statistics
        total_users = User.objects.count()
        total_students = User.objects.filter(role='student').count()
        total_teachers = User.objects.filter(role='teacher').count()
        total_admins = User.objects.filter(role='admin').count()
        
        # Course statistics
        total_courses = Course.objects.count()
        published_courses = Course.objects.filter(is_published=True).count()
        draft_courses = Course.objects.filter(is_published=False, is_submitted_for_review=False).count()
        pending_review = Course.objects.filter(is_submitted_for_review=True, is_published=False).count()
        
        # Enrollment statistics
        total_enrollments = Enrollment.objects.count()
        active_enrollments = Enrollment.objects.filter(is_active=True).count()
        
        # Teacher verification
        pending_teacher_verifications = TeacherProfile.objects.filter(
            verification_status='pending'
        ).count()
        
        # Recent signups (last 10)
        recent_users = User.objects.order_by('-date_joined')[:10]
        recent_signups = []
        for user in recent_users:
            recent_signups.append({
                'id': user.id,
                'name': user.get_full_name() or user.username,
                'email': user.email,
                'role': user.role,
                'date_joined': user.date_joined.isoformat()
            })
        
        # Recent enrollments (last 10)
        recent_enroll_objs = Enrollment.objects.select_related('user', 'course').order_by('-enrolled_at')[:10]
        recent_enrollments = []
        for enrollment in recent_enroll_objs:
            recent_enrollments.append({
                'id': enrollment.id,
                'student_name': enrollment.user.get_full_name() or enrollment.user.username,
                'course_title': enrollment.course.title,
                'enrolled_at': enrollment.enrolled_at.isoformat()
            })
        
        # Prepare response
        data = {
            'total_users': total_users,
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_admins': total_admins,
            'total_courses': total_courses,
            'published_courses': published_courses,
            'draft_courses': draft_courses,
            'pending_review': pending_review,
            'total_enrollments': total_enrollments,
            'active_enrollments': active_enrollments,
            'pending_teacher_verifications': pending_teacher_verifications,
            'recent_signups': recent_signups,
            'recent_enrollments': recent_enrollments
        }
        
        return Response({'data': data}, status=status.HTTP_200_OK)


class UserManagementView(APIView):
    """
    List and manage users
    
    GET /api/admin/users?page=1&limit=10&role=all&search=
    """
    permission_classes = [IsAdmin]
    
    def get(self, request):
        # Get query params
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        role_filter = request.GET.get('role', 'all')
        search = request.GET.get('search', '')
        
        # Base queryset
        queryset = User.objects.all()
        
        # Apply role filter
        if role_filter and role_filter != 'all':
            queryset = queryset.filter(role=role_filter)
        
        # Apply search
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Order by
        queryset = queryset.order_by('-date_joined')
        
        # Paginate
        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        users = queryset[start:end]
        
        # Serialize
        serializer = UserManagementSerializer(users, many=True)
        
        return Response({
            'data': serializer.data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'totalPages': (total + limit - 1) // limit
            }
        }, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    """
    Get, update, or delete a user
    
    GET /api/admin/users/{id}
    PUT /api/admin/users/{id}
    DELETE /api/admin/users/{id}
    """
    permission_classes = [IsAdmin]
    
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        
        # Get detailed profile based on role
        if user.role == 'student':
            try:
                profile = StudentProfile.objects.get(user=user)
                serializer = StudentDetailSerializer(profile)
            except StudentProfile.DoesNotExist:
                serializer = UserBasicSerializer(user)
        elif user.role == 'teacher':
            try:
                profile = TeacherProfile.objects.get(user=user)
                serializer = TeacherDetailSerializer(profile)
            except TeacherProfile.DoesNotExist:
                serializer = UserBasicSerializer(user)
        else:
            serializer = UserBasicSerializer(user)
        
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    
    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        
        # Prevent admin from modifying themselves
        if user.id == request.user.id:
            return Response(
                {'message': 'You cannot modify your own account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response(
                {'message': 'Invalid data', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        
        response_serializer = UserManagementSerializer(user)
        return Response({
            'message': 'User updated successfully',
            'data': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        
        # Prevent admin from deleting themselves
        if user.id == request.user.id:
            return Response(
                {'message': 'You cannot delete your own account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.delete()
        return Response(
            {'message': 'User deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


class TeacherVerificationListView(APIView):
    """
    List teacher verification applications
    
    GET /api/admin/teacher-verifications?status=pending
    """
    permission_classes = [IsAdmin]
    
    def get(self, request):
        # Get query params
        status_filter = request.GET.get('status', 'pending')
        
        # Base queryset
        queryset = TeacherProfile.objects.select_related('user')
        
        # Apply status filter
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(verification_status=status_filter)
        
        # Order by
        queryset = queryset.order_by('-user__date_joined')
        
        # Serialize
        serializer = TeacherVerificationSerializer(queryset, many=True)
        
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class TeacherVerificationActionView(APIView):
    """
    Approve or reject teacher verification
    
    POST /api/admin/teacher-verifications/{id}/review
    """
    permission_classes = [IsAdmin]
    
    def post(self, request, teacher_id):
        teacher_profile = get_object_or_404(TeacherProfile, user__id=teacher_id)
        
        serializer = TeacherVerificationActionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'message': 'Invalid data', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        action = serializer.validated_data['action']
        
        if action == 'approve':
            teacher_profile.verification_status = 'approved'
            teacher_profile.is_verified = True
            teacher_profile.verified_at = timezone.now()
            teacher_profile.rejection_reason = ''
            teacher_profile.save()
            
            return Response(
                {'message': 'Teacher verified successfully'},
                status=status.HTTP_200_OK
            )
        
        elif action == 'reject':
            teacher_profile.verification_status = 'rejected'
            teacher_profile.is_verified = False
            teacher_profile.rejection_reason = serializer.validated_data.get('rejection_reason', '')
            teacher_profile.save()
            
            return Response(
                {'message': 'Teacher verification rejected'},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'message': 'Invalid action'},
            status=status.HTTP_400_BAD_REQUEST
        )


class CourseReviewListView(APIView):
    """
    List courses pending review
    
    GET /api/admin/course-reviews?status=pending
    """
    permission_classes = [IsAdmin]
    
    def get(self, request):
        # Get query params
        status_filter = request.GET.get('status', 'pending')
        
        # Base queryset
        queryset = Course.objects.select_related('published_by')
        
        # Apply status filter
        if status_filter == 'pending':
            queryset = queryset.filter(is_submitted_for_review=True, is_published=False)
        elif status_filter == 'published':
            queryset = queryset.filter(is_published=True)
        elif status_filter == 'draft':
            queryset = queryset.filter(is_published=False, is_submitted_for_review=False)
        
        # Order by
        queryset = queryset.order_by('-published_date', '-id')
        
        # Serialize
        serializer = CourseReviewSerializer(queryset, many=True)
        
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class CourseReviewActionView(APIView):
    """
    Approve or reject course for publication
    
    POST /api/admin/course-reviews/{id}/review
    """
    permission_classes = [IsAdmin]
    
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        
        serializer = CourseReviewActionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'message': 'Invalid data', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        action = serializer.validated_data['action']
        
        if action == 'approve':
            course.is_published = True
            course.is_submitted_for_review = False
            course.published_date = timezone.now()
            course.save()
            
            return Response(
                {'message': 'Course approved and published successfully'},
                status=status.HTTP_200_OK
            )
        
        elif action == 'reject':
            course.is_submitted_for_review = False
            # Note: Could add rejection_reason field to Course model
            course.save()
            
            return Response(
                {'message': 'Course review rejected'},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'message': 'Invalid action'},
            status=status.HTTP_400_BAD_REQUEST
        )


class CourseManagementView(APIView):
    """
    List and manage all courses
    
    GET /api/admin/courses?page=1&limit=10&status=all&search=
    """
    permission_classes = [IsAdmin]
    
    def get(self, request):
        # Get query params
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        status_filter = request.GET.get('status', 'all')
        search = request.GET.get('search', '')
        
        # Base queryset
        queryset = Course.objects.select_related('published_by')
        
        # Apply status filter
        if status_filter == 'published':
            queryset = queryset.filter(is_published=True)
        elif status_filter == 'draft':
            queryset = queryset.filter(is_published=False, is_submitted_for_review=False)
        elif status_filter == 'under_review':
            queryset = queryset.filter(is_submitted_for_review=True, is_published=False)
        
        # Apply search
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(published_by__username__icontains=search) |
                Q(published_by__email__icontains=search)
            )
        
        # Order by
        queryset = queryset.order_by('-published_date', '-id')
        
        # Paginate
        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        courses = queryset[start:end]
        
        # Serialize
        serializer = CourseManagementSerializer(courses, many=True)
        
        return Response({
            'data': serializer.data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'totalPages': (total + limit - 1) // limit
            }
        }, status=status.HTTP_200_OK)


class CourseStatusUpdateView(APIView):
    """
    Update course publication status
    
    PUT /api/admin/courses/{id}/status
    """
    permission_classes = [IsAdmin]
    
    def put(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        
        serializer = CourseStatusUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'message': 'Invalid data', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if 'is_published' in serializer.validated_data:
            course.is_published = serializer.validated_data['is_published']
            if course.is_published and not course.published_date:
                course.published_date = timezone.now()
        
        if 'is_submitted_for_review' in serializer.validated_data:
            course.is_submitted_for_review = serializer.validated_data['is_submitted_for_review']
        
        course.save()
        
        return Response(
            {'message': 'Course status updated successfully'},
            status=status.HTTP_200_OK
        )


class EnrollmentManagementView(APIView):
    """
    List and manage enrollments
    
    GET /api/admin/enrollments?page=1&limit=10&course_id=&user_id=
    """
    permission_classes = [IsAdmin]
    
    def get(self, request):
        # Get query params
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        course_id = request.GET.get('course_id')
        user_id = request.GET.get('user_id')
        
        # Base queryset
        queryset = Enrollment.objects.select_related('user', 'course')
        
        # Apply filters
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Order by
        queryset = queryset.order_by('-enrolled_at')
        
        # Paginate
        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        enrollments = queryset[start:end]
        
        # Serialize
        serializer = EnrollmentManagementSerializer(enrollments, many=True)
        
        return Response({
            'data': serializer.data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'totalPages': (total + limit - 1) // limit
            }
        }, status=status.HTTP_200_OK)
