"""
Forum API Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q, Count

from lms.models import ForumPost, ForumComment, ForumLike
from api.serializers import ForumPostSerializer, ForumCommentSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def forum_posts_list(request):
    """
    GET: List all forum posts with pagination and filters
    POST: Create a new forum post
    """
    if request.method == 'GET':
        # Get query parameters
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 12))
        search = request.GET.get('search', '')
        tags = request.GET.getlist('tags[]')  # Can be multiple tags
        sort_by = request.GET.get('sortBy', 'recent')
        
        # Base queryset
        queryset = ForumPost.objects.all()
        
        # Apply search filter
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        # Apply tags filter
        if tags:
            # Filter posts that have any of the selected tags
            for tag in tags:
                queryset = queryset.filter(tags__contains=tag)
        
        # Apply sorting
        if sort_by == 'popular':
            # Sort by likes count
            queryset = queryset.annotate(likes_count=Count('likes')).order_by('-likes_count', '-created_at')
        else:  # recent
            queryset = queryset.order_by('-is_pinned', '-created_at')
        
        # Paginate
        paginator = Paginator(queryset, limit)
        page_obj = paginator.get_page(page)
        
        # Serialize
        serializer = ForumPostSerializer(page_obj.object_list, many=True, context={'request': request})
        
        return Response({
            'success': True,
            'data': serializer.data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': paginator.count,
                'totalPages': paginator.num_pages
            }
        })
    
    elif request.method == 'POST':
        # Create new post
        serializer = ForumPostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response({
                'success': True,
                'message': 'Forum post created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def forum_tags(request):
    """
    GET: Get all unique tags used in forum posts
    """
    # Get all posts and extract unique tags
    posts = ForumPost.objects.all()
    all_tags = set()
    
    for post in posts:
        if post.tags:
            all_tags.update(post.tags)
    
    return Response({
        'success': True,
        'data': sorted(list(all_tags))
    })


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def forum_post_detail(request, post_id):
    """
    GET: Get a specific forum post
    PUT: Update a forum post (author only)
    DELETE: Delete a forum post (author only)
    """
    try:
        post = ForumPost.objects.get(pk=post_id)
    except ForumPost.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Forum post not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ForumPostSerializer(post, context={'request': request})
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    elif request.method == 'PUT':
        # Check if user is the author
        if post.author != request.user:
            return Response({
                'success': False,
                'message': 'You can only edit your own posts'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ForumPostSerializer(post, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Post updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Check if user is the author or admin
        if post.author != request.user and not request.user.is_staff:
            return Response({
                'success': False,
                'message': 'You can only delete your own posts'
            }, status=status.HTTP_403_FORBIDDEN)
        
        post.delete()
        return Response({
            'success': True,
            'message': 'Post deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def forum_post_comments(request, post_id):
    """
    GET: Get all comments for a forum post
    POST: Create a new comment on a forum post
    """
    try:
        post = ForumPost.objects.get(pk=post_id)
    except ForumPost.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Forum post not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        # Get only root comments (no parent), replies will be nested
        comments = ForumComment.objects.filter(post=post, parent=None)
        serializer = ForumCommentSerializer(comments, many=True, context={'request': request})
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    elif request.method == 'POST':
        serializer = ForumCommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Handle parent_id if it's a reply
            parent_id = request.data.get('parentId')
            parent = None
            if parent_id:
                try:
                    parent = ForumComment.objects.get(pk=parent_id)
                except ForumComment.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': 'Parent comment not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            serializer.save(author=request.user, post=post, parent=parent)
            return Response({
                'success': True,
                'message': 'Comment created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def forum_post_like(request, post_id):
    """
    POST: Like a forum post
    DELETE: Unlike a forum post
    """
    try:
        post = ForumPost.objects.get(pk=post_id)
    except ForumPost.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Forum post not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        # Create like if it doesn't exist
        like, created = ForumLike.objects.get_or_create(user=request.user, post=post)
        
        if created:
            return Response({
                'success': True,
                'message': 'Post liked successfully'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': True,
                'message': 'Post already liked'
            })
    
    elif request.method == 'DELETE':
        # Remove like
        try:
            like = ForumLike.objects.get(user=request.user, post=post)
            like.delete()
            return Response({
                'success': True,
                'message': 'Post unliked successfully'
            }, status=status.HTTP_204_NO_CONTENT)
        except ForumLike.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Like not found'
            }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def forum_comment_like(request, comment_id):
    """
    POST: Like a forum comment
    DELETE: Unlike a forum comment
    """
    try:
        comment = ForumComment.objects.get(pk=comment_id)
    except ForumComment.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Comment not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        # Create like if it doesn't exist
        like, created = ForumLike.objects.get_or_create(user=request.user, comment=comment)
        
        if created:
            return Response({
                'success': True,
                'message': 'Comment liked successfully'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': True,
                'message': 'Comment already liked'
            })
    
    elif request.method == 'DELETE':
        # Remove like
        try:
            like = ForumLike.objects.get(user=request.user, comment=comment)
            like.delete()
            return Response({
                'success': True,
                'message': 'Comment unliked successfully'
            }, status=status.HTTP_204_NO_CONTENT)
        except ForumLike.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Like not found'
            }, status=status.HTTP_404_NOT_FOUND)
