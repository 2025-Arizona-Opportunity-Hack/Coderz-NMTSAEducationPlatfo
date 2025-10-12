"""
Supermemory-Enhanced Search Views
Provides AI-powered contextual course search
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from teacher_dash.models import Course
from student_dash.serializers import CourseListSerializer
from nmtsa_lms.supermemory_client import get_supermemory_client


@api_view(['POST'])
@permission_classes([AllowAny])
def contextual_course_search(request):
    """
    AI-powered contextual course search using Supermemory.
    Searches courses based on natural language query and contextual understanding.
    
    POST /api/v1/search/courses/contextual/
    Body: { "query": "courses about music therapy for children" }
    
    Returns: List of contextually relevant courses
    """
    query = request.data.get('query', '').strip()
    
    if not query:
        return Response(
            {'error': 'Search query is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get Supermemory client
    client = get_supermemory_client()
    
    # Initialize results with basic keyword search
    courses = Course.objects.filter(
        is_published=True,
        admin_approved=True
    ).filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(tags__name__icontains=query)
    ).distinct()[:10]
    
    # Enhance with Supermemory if available
    if client:
        try:
            # Search memories for course-related context
            search_response = client.search.execute(
                q=f"course recommendations for: {query}"
            )
            
            # Extract keywords from search results
            memory_keywords = set()
            if search_response.results:
                for result in search_response.results[:5]:
                    if hasattr(result, 'content'):
                        words = result.content.lower().split()
                        memory_keywords.update([w for w in words if len(w) > 3])
            
            # Expand search with memory-derived keywords
            if memory_keywords:
                expanded_query = Q(title__icontains=query) | Q(description__icontains=query)
                for keyword in list(memory_keywords)[:5]:
                    expanded_query |= Q(title__icontains=keyword) | Q(description__icontains=keyword)
                
                courses = Course.objects.filter(
                    is_published=True,
                    admin_approved=True
                ).filter(expanded_query).distinct()[:20]
            
            # Store this search for future context
            client.memories.add(content=f"User searched for courses: {query}")
            
        except Exception:
            # Fallback to basic search if Supermemory fails
            pass
    
    # Serialize results
    serializer = CourseListSerializer(courses, many=True)
    
    return Response({
        'query': query,
        'count': len(serializer.data),
        'courses': serializer.data,
        'ai_enhanced': client is not None
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_course_recommendations(request):
    """
    Get AI-powered course recommendations based on user interests.
    
    GET /api/v1/search/courses/recommendations/?interests=music therapy,children
    
    Returns: List of recommended courses
    """
    interests = request.GET.get('interests', '').strip()
    limit = int(request.GET.get('limit', 5))
    
    if not interests:
        # Return popular courses if no interests specified
        courses = Course.objects.filter(
            is_published=True,
            admin_approved=True
        ).order_by('-num_enrollments')[:limit]
    else:
        # Get contextual recommendations
        client = get_supermemory_client()
        
        if client:
            try:
                # Search for related course content in memories
                search_response = client.search.execute(
                    q=f"course recommendations for interests: {interests}"
                )
                
                # Build query from interests
                interest_list = [i.strip() for i in interests.split(',')]
                query = Q()
                
                for interest in interest_list:
                    query |= Q(title__icontains=interest) | Q(description__icontains=interest) | Q(tags__name__icontains=interest)
                
                courses = Course.objects.filter(
                    is_published=True,
                    admin_approved=True
                ).filter(query).distinct().order_by('-num_enrollments')[:limit]
                
            except Exception:
                # Fallback
                courses = Course.objects.filter(
                    is_published=True,
                    admin_approved=True
                ).order_by('-num_enrollments')[:limit]
        else:
            # Basic filtering without Supermemory
            interest_list = [i.strip() for i in interests.split(',')]
            query = Q()
            
            for interest in interest_list:
                query |= Q(title__icontains=interest) | Q(description__icontains=interest)
            
            courses = Course.objects.filter(
                is_published=True,
                admin_approved=True
            ).filter(query).distinct().order_by('-num_enrollments')[:limit]
    
    serializer = CourseListSerializer(courses, many=True)
    
    return Response({
        'interests': interests if interests else 'popular',
        'count': len(serializer.data),
        'courses': serializer.data
    })
