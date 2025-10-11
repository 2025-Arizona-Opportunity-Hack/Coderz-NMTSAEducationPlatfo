"""
Course API Views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404

from teacher_dash.models import Course, Module
from authentication.models import Enrollment
from lms.models import CompletedLesson
from api.serializers import (
    CourseSerializer, 
    CourseDetailSerializer, 
    EnrollmentSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Custom pagination class matching frontend expectations"""
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'data': data,
            'pagination': {
                'page': self.page.number,
                'limit': self.page.paginator.per_page,
                'total': self.page.paginator.count,
                'totalPages': self.page.paginator.num_pages,
            }
        })


class CourseListView(APIView):
    """
    List courses with filtering and search
    
    GET /api/courses?page=1&limit=10&search=&category=&difficulty=&sortBy=newest
    """
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get(self, request):
        # Base queryset - only published courses
        queryset = Course.objects.filter(is_published=True).select_related(
            'published_by'
        ).prefetch_related('modules__lessons')
        
        # Search
        search = request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Category filter
        category = request.GET.get('category', '').strip()
        if category:
            queryset = queryset.filter(tags__name__iexact=category)
        
        # Difficulty filter
        difficulty = request.GET.get('difficulty', '').strip()
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Price filters
        min_price = request.GET.get('minPrice')
        max_price = request.GET.get('maxPrice')
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        # Credits filters
        min_credits = request.GET.get('minCredits')
        max_credits = request.GET.get('maxCredits')
        if min_credits:
            try:
                queryset = queryset.filter(credits__gte=int(min_credits))
            except ValueError:
                pass
        if max_credits:
            try:
                queryset = queryset.filter(credits__lte=int(max_credits))
            except ValueError:
                pass
        
        # Rating filter
        min_rating = request.GET.get('minRating')
        if min_rating:
            try:
                queryset = queryset.filter(rating__gte=float(min_rating))
            except ValueError:
                pass
        
        # Sorting
        sort_by = request.GET.get('sortBy', 'newest')
        sort_order = request.GET.get('sortOrder', 'desc')
        
        if sort_by == 'popularity':
            order_field = 'num_enrollments'
        elif sort_by == 'rating':
            order_field = 'rating'
        elif sort_by == 'title':
            order_field = 'title'
        else:  # newest
            order_field = 'published_date'
        
        if sort_order == 'asc':
            queryset = queryset.order_by(order_field)
        else:
            queryset = queryset.order_by(f'-{order_field}')
        
        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = CourseSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        
        serializer = CourseSerializer(queryset, many=True, context={'request': request})
        return Response({'data': serializer.data})


class CourseDetailView(APIView):
    """
    Get basic course details
    
    GET /api/courses/{id}
    """
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        course = get_object_or_404(
            Course.objects.select_related('published_by'),
            pk=pk,
            is_published=True
        )
        serializer = CourseSerializer(course, context={'request': request})
        return Response(serializer.data)


class CourseFullDetailView(APIView):
    """
    Get full course details with modules and lessons
    
    GET /api/courses/{id}/detail
    """
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        course = get_object_or_404(
            Course.objects.select_related('published_by')
            .prefetch_related(
                'modules__lessons__video',
                'modules__lessons__blog'
            ),
            pk=pk,
            is_published=True
        )
        
        # Get completed lessons if user is enrolled
        completed_lessons = set()
        if request.user.is_authenticated:
            try:
                enrollment = Enrollment.objects.get(
                    user=request.user,
                    course=course,
                    is_active=True
                )
                completed_lessons = set(
                    CompletedLesson.objects.filter(enrollment=enrollment)
                    .values_list('lesson_id', flat=True)
                )
            except Enrollment.DoesNotExist:
                pass
        
        serializer = CourseDetailSerializer(
            course, 
            context={
                'request': request,
                'completed_lessons': completed_lessons
            }
        )
        return Response(serializer.data)


class CategoryListView(APIView):
    """
    Get list of all course categories
    
    GET /api/courses/categories
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Get unique categories from tags
        categories = Course.objects.filter(
            is_published=True
        ).values_list('tags__name', flat=True).distinct()
        
        # Filter out None and empty strings
        categories = [cat for cat in categories if cat]
        
        return Response({'data': sorted(categories)})


class FeaturedCoursesView(APIView):
    """
    Get featured courses
    
    GET /api/courses/featured?limit=6
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        limit = int(request.GET.get('limit', 6))
        
        # Get top enrolled published courses
        courses = Course.objects.filter(
            is_published=True
        ).select_related('published_by').order_by(
            '-num_enrollments', '-rating'
        )[:limit]
        
        serializer = CourseSerializer(courses, many=True, context={'request': request})
        return Response({'data': serializer.data})


class EnrollmentView(APIView):
    """
    Enroll in or unenroll from a course
    
    POST /api/courses/{id}/enroll - Enroll in course
    DELETE /api/courses/{id}/enroll - Unenroll from course
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk, is_published=True)
        
        # Check if already enrolled
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={
                'is_active': True,
                'progress_percentage': 0
            }
        )
        
        if not created:
            if not enrollment.is_active:
                enrollment.is_active = True
                enrollment.save()
            else:
                return Response(
                    {'message': 'Already enrolled in this course'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Increment enrollment count
            course.num_enrollments += 1
            course.save(update_fields=['num_enrollments'])
        
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        
        try:
            enrollment = Enrollment.objects.get(
                user=request.user,
                course=course,
                is_active=True
            )
            enrollment.is_active = False
            enrollment.save()
            
            # Decrement enrollment count
            if course.num_enrollments > 0:
                course.num_enrollments -= 1
                course.save(update_fields=['num_enrollments'])
            
            return Response(
                {'message': 'Successfully unenrolled from course'},
                status=status.HTTP_200_OK
            )
        except Enrollment.DoesNotExist:
            return Response(
                {'message': 'Not enrolled in this course'},
                status=status.HTTP_404_NOT_FOUND
            )


class CourseReviewsView(APIView):
    """
    Get course reviews (placeholder - to be implemented)
    
    GET /api/courses/{id}/reviews?page=1&limit=10
    """
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        # Placeholder - reviews model to be implemented
        return Response({
            'data': [],
            'pagination': {
                'page': 1,
                'limit': 10,
                'total': 0,
                'totalPages': 0
            }
        })
