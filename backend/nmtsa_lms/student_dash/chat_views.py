"""
Chat API Views
Provides chat functionality with Supermemory AI integration.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import uuid
import json

from nmtsa_lms.supermemory_client import get_supermemory_client


# Mock data storage (in production, this would be in the database)
MOCK_CONVERSATIONS = {}
MOCK_MESSAGES = {}
MOCK_TYPING_STATUS = {}


@api_view(['GET'])
@permission_classes([AllowAny])
def get_conversations(request):
    """
    Get all conversations (no authentication required for info bot).
    Query params: page, limit
    """
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 20))
    
    # Generic user ID for anonymous chat
    user_id = 'guest'
    
    # Generate mock conversations
    mock_conversations = [
        {
            'id': str(uuid.uuid4()),
            'participantIds': [user_id, 'assistant'],
            'participants': [
                {
                    'id': user_id,
                    'email': 'guest@nmtsa.com',
                    'fullName': 'Guest User',
                    'role': 'student',
                    'avatarUrl': None,
                },
                {
                    'id': 'assistant',
                    'email': 'assistant@nmtsa.com',
                    'fullName': 'NMTSA Assistant',
                    'role': 'admin',
                    'avatarUrl': 'https://i.pravatar.cc/150?img=1',
                }
            ],
            'lastMessage': {
                'id': str(uuid.uuid4()),
                'content': 'Hello! I\'m your NMTSA Learn assistant. Ask me about courses, features, or how to get started!',
                'senderId': 'assistant',
                'timestamp': (timezone.now() - timedelta(minutes=5)).isoformat(),
                'isRead': False,
            },
            'unreadCount': 0,
            'updatedAt': timezone.now().isoformat(),
        }
    ]
    
    # Pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_conversations = mock_conversations[start:end]
    
    return Response({
        'data': paginated_conversations,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': len(mock_conversations),
            'totalPages': (len(mock_conversations) + limit - 1) // limit,
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_messages(request, conversation_id):
    """
    Get messages for a specific conversation (no auth required).
    Query params: page, limit
    """
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 50))
    
    user_id = 'guest'
    
    # Generate mock messages
    mock_messages = [
        {
            'id': str(uuid.uuid4()),
            'content': 'Hello! I have a question about the course material.',
            'senderId': user_id,
            'sender': {
                'id': user_id,
                'fullName': f"{request.user.first_name} {request.user.last_name}",
                'avatarUrl': None,
                'role': 'student',
            },
            'recipientId': 'user-2',
            'conversationId': conversation_id,
            'isRead': True,
            'timestamp': (timezone.now() - timedelta(minutes=10)).isoformat(),
            'createdAt': (timezone.now() - timedelta(minutes=10)).isoformat(),
        },
        {
            'id': str(uuid.uuid4()),
            'content': 'Of course! I\'m here to help. What would you like to know?',
            'senderId': 'user-2',
            'sender': {
                'id': 'user-2',
                'fullName': 'Dr. Jane Smith',
                'avatarUrl': 'https://i.pravatar.cc/150?img=1',
                'role': 'instructor',
            },
            'recipientId': user_id,
            'conversationId': conversation_id,
            'isRead': True,
            'timestamp': (timezone.now() - timedelta(minutes=9)).isoformat(),
            'createdAt': (timezone.now() - timedelta(minutes=9)).isoformat(),
        },
        {
            'id': str(uuid.uuid4()),
            'content': 'I\'m having trouble understanding the neurologic music therapy techniques.',
            'senderId': user_id,
            'sender': {
                'id': user_id,
                'fullName': f"{request.user.first_name} {request.user.last_name}",
                'avatarUrl': None,
                'role': 'student',
            },
            'recipientId': 'user-2',
            'conversationId': conversation_id,
            'isRead': True,
            'timestamp': (timezone.now() - timedelta(minutes=7)).isoformat(),
            'createdAt': (timezone.now() - timedelta(minutes=7)).isoformat(),
        },
        {
            'id': str(uuid.uuid4()),
            'content': 'Let me explain. NMT techniques are evidence-based interventions. Would you like me to break down specific techniques?',
            'senderId': 'user-2',
            'sender': {
                'id': 'user-2',
                'fullName': 'Dr. Jane Smith',
                'avatarUrl': 'https://i.pravatar.cc/150?img=1',
                'role': 'instructor',
            },
            'recipientId': user_id,
            'conversationId': conversation_id,
            'isRead': False,
            'timestamp': (timezone.now() - timedelta(minutes=5)).isoformat(),
            'createdAt': (timezone.now() - timedelta(minutes=5)).isoformat(),
        },
    ]
    
    # Pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_messages = mock_messages[start:end]
    
    return Response({
        'data': paginated_messages,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': len(mock_messages),
            'totalPages': (len(mock_messages) + limit - 1) // limit,
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def send_message(request):
    """
    Send a new message and get AI-powered response using Supermemory.
    Body: { content, conversationId, recipientId? }
    """
    content = request.data.get('content', '').strip()
    conversation_id = request.data.get('conversationId')
    recipient_id = request.data.get('recipientId')
    
    if not content:
        return Response(
            {'error': 'Message content is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user_id = 'guest'
    
    # Create user message
    user_message = {
        'id': str(uuid.uuid4()),
        'content': content,
        'senderId': user_id,
        'sender': {
            'id': user_id,
            'fullName': 'You',
            'avatarUrl': None,
            'role': 'student',
        },
        'recipientId': recipient_id,
        'conversationId': conversation_id,
        'isRead': True,
        'timestamp': timezone.now().isoformat(),
        'createdAt': timezone.now().isoformat(),
    }
    
    # Process message with Supermemory for context-aware response
    client = get_supermemory_client()
    ai_response_content = "Thank you for your message! I'm here to help you with information about NMTSA Learn platform and courses."
    
    if client:
        try:
            # Search for relevant context in memories
            search_response = client.search.execute(q=content)
            
            # Store this interaction as memory
            client.memories.add(content=f"User asked: {content}")
            
            # Generate contextual response based on search results
            if search_response.results:
                # Get top results content
                context_items = [r.content for r in search_response.results[:3] if hasattr(r, 'content')]
                if context_items:
                    context = "\n".join(context_items)
                    ai_response_content = f"Based on what I know: {context}\n\nHow else can I assist you?"
                else:
                    # Use fallback responses
                    ai_response_content = _get_fallback_response(content)
            else:
                # No results, use fallback
                ai_response_content = _get_fallback_response(content)
        except Exception:
            # Fallback if Supermemory fails
            ai_response_content = _get_fallback_response(content)
    else:
        # No client, use fallback
        ai_response_content = _get_fallback_response(content)


def _get_fallback_response(content: str) -> str:
    """Generate fallback response based on content keywords"""
    content_lower = content.lower()
    
    if any(keyword in content_lower for keyword in ['course', 'class', 'learn']):
        return "We offer a variety of music therapy courses! You can browse our catalog to find courses that match your interests. Would you like me to help you find specific courses?"
    elif any(keyword in content_lower for keyword in ['start', 'begin', 'how to']):
        return "Getting started is easy! Browse our course catalog, click on a course you're interested in, and enroll. Many courses are free to start. What area of music therapy interests you most?"
    elif any(keyword in content_lower for keyword in ['help', 'support']):
        return "I'm here to help! You can ask me about:\n• Available courses\n• How to enroll\n• Platform features\n• Music therapy topics\n\nWhat would you like to know?"
    else:
        return "Thank you for your message! I'm here to help you with information about NMTSA Learn. You can ask me about courses, how to get started, or any questions about music therapy education."
    
    # Create AI assistant response
    assistant_message = {
        'id': str(uuid.uuid4()),
        'content': ai_response_content,
        'senderId': 'assistant',
        'sender': {
            'id': 'assistant',
            'fullName': 'NMTSA Assistant',
            'avatarUrl': 'https://i.pravatar.cc/150?img=1',
            'role': 'admin',
        },
        'recipientId': user_id,
        'conversationId': conversation_id,
        'isRead': False,
        'timestamp': (timezone.now() + timedelta(seconds=1)).isoformat(),
        'createdAt': (timezone.now() + timedelta(seconds=1)).isoformat(),
    }
    
    # Return both messages
    return Response({
        'userMessage': user_message,
        'assistantMessage': assistant_message
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def mark_as_read(request):
    """
    Mark messages as read.
    Body: { messageIds: string[] }
    """
    message_ids = request.data.get('messageIds', [])
    
    if not message_ids:
        return Response(
            {'message': 'Message IDs are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # In production, update the database
    # For now, just return success
    return Response({'message': 'Messages marked as read'})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_typing_status(request, conversation_id):
    """
    Get typing status for a conversation.
    """
    # Return mock typing status (empty for now)
    typing_statuses = []
    
    return Response({'data': typing_statuses})


@api_view(['POST'])
@permission_classes([AllowAny])
def update_typing_status(request, conversation_id):
    """
    Update typing status.
    Body: { isTyping: boolean }
    """
    is_typing = request.data.get('isTyping', False)
    user_id = str(request.user.id)
    
    # Store typing status (in production, use Redis or similar)
    global MOCK_TYPING_STATUS
    MOCK_TYPING_STATUS[f"{conversation_id}:{user_id}"] = {
        'userId': user_id,
        'conversationId': conversation_id,
        'isTyping': is_typing,
        'timestamp': timezone.now().isoformat(),
    }
    
    return Response({'message': 'Typing status updated'})


@api_view(['POST'])
@permission_classes([AllowAny])
def create_conversation(request):
    """
    Create or get a conversation with a specific user.
    Body: { participantId: string }
    """
    participant_id = request.data.get('participantId')
    
    if not participant_id:
        return Response(
            {'message': 'Participant ID is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user_id = str(request.user.id)
    
    # Create mock conversation
    conversation = {
        'id': str(uuid.uuid4()),
        'participantIds': [user_id, participant_id],
        'participants': [
            {
                'id': user_id,
                'email': request.user.email,
                'fullName': f"{request.user.first_name} {request.user.last_name}",
                'role': 'student',
                'avatarUrl': None,
            },
            {
                'id': participant_id,
                'email': 'other@example.com',
                'fullName': 'Other User',
                'role': 'instructor',
                'avatarUrl': 'https://i.pravatar.cc/150?img=3',
            }
        ],
        'lastMessage': None,
        'unreadCount': 0,
        'updatedAt': timezone.now().isoformat(),
    }
    
    return Response({'data': conversation}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_conversation(request, conversation_id):
    """
    Delete a conversation.
    """
    # In production, delete from database
    # For now, just return success
    return Response({'message': 'Conversation deleted'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_unread_count(request):
    """
    Get unread message count for the current user.
    """
    # Return mock unread count
    unread_count = 2
    
    return Response({'data': {'count': unread_count}})
