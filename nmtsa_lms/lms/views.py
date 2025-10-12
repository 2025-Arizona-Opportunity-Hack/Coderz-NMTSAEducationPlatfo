from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from authentication.decorators import login_required
import json
from datetime import datetime, timedelta
import time
from .supermemory_client import get_supermemory_client

# Mock data storage (replace with database queries in production)
MOCK_MESSAGES = []
MOCK_TYPING_USERS = {}


@require_http_methods(["GET"])
def chat_get_rooms(request):
	"""
	Get list of chat rooms for the current user.
	Returns mock data for now.
	Available to all users (authenticated or not).
	"""
	session_user = request.session.get('user', {})
	user_id = session_user.get('user_id', 'guest')
	user_name = session_user.get('full_name', 'Guest')
	
	# Mock chat rooms
	mock_rooms = [
		{
			'id': 1,
			'name': 'Support Chat',
			'room_type': 'support',
			'participants': ['Admin Support', user_name],
			'last_message': {
				'content': 'How can I help you today?',
				'timestamp': (timezone.now() - timedelta(hours=1)).isoformat(),
				'sender': 'Admin Support'
			},
			'unread_count': 1,
			'is_active': True
		},
		{
			'id': 2,
			'name': 'Course Discussion',
			'room_type': 'group',
			'participants': ['Teacher', 'Student 1', 'Student 2', user_name],
			'last_message': {
				'content': 'Great lesson today!',
				'timestamp': (timezone.now() - timedelta(hours=3)).isoformat(),
				'sender': 'Student 1'
			},
			'unread_count': 0,
			'is_active': True
		}
	]
	
	return JsonResponse({
		'success': True,
		'rooms': mock_rooms
	})


@require_http_methods(["GET"])
def chat_get_messages(request, room_id):
	"""
	Get message history for a specific room.
	Returns mock data for now.
	Available to all users (authenticated or not).
	"""
	session_user = request.session.get('user', {})
	user_id = session_user.get('user_id', 'guest')
	user_name = session_user.get('full_name', 'You')
	
	# Mock messages
	mock_messages = [
		{
			'id': 1,
			'sender': 'Admin Support',
			'sender_id': 999,
			'content': 'Hello! Welcome to NMTSA LMS support chat.',
			'timestamp': (timezone.now() - timedelta(hours=2)).isoformat(),
			'is_own_message': False,
			'message_type': 'system'
		},
		{
			'id': 2,
			'sender': 'Admin Support',
			'sender_id': 999,
			'content': 'How can I help you today?',
			'timestamp': (timezone.now() - timedelta(hours=1, minutes=30)).isoformat(),
			'is_own_message': False,
			'message_type': 'text'
		},
	]
	
	# Add any messages sent during this session
	for msg in MOCK_MESSAGES:
		if msg.get('room_id') == int(room_id):
			mock_messages.append({
				'id': msg['id'],
				'sender': user_name,
				'sender_id': user_id,
				'content': msg['content'],
				'timestamp': msg['timestamp'],
				'is_own_message': True,
				'message_type': 'text'
			})
	
	return JsonResponse({
		'success': True,
		'messages': mock_messages
	})


@require_http_methods(["POST"])
def chat_send_message(request, room_id):
	"""
	Send a new message to a chat room.
	Validates and stores (mock for now).
	Available to all users (authenticated or not).
	"""
	try:
		data = json.loads(request.body)
		content = data.get('content', '').strip()
		
		# Validation
		if not content:
			return JsonResponse({
				'success': False,
				'error': 'Message cannot be empty'
			}, status=400)
		
		if len(content) > 2000:
			return JsonResponse({
				'success': False,
				'error': 'Message too long (max 2000 characters)'
			}, status=400)
		
		session_user = request.session.get('user', {})
		user_id = session_user.get('user_id', 'guest')
		user_name = session_user.get('full_name', 'Guest')
		
		# Simulate network delay
		time.sleep(0.1)
		
		# Store message (mock)
		message = {
			'id': len(MOCK_MESSAGES) + 100,
			'room_id': int(room_id),
			'content': content,
			'sender': user_name,
			'sender_id': user_id,
			'timestamp': timezone.now().isoformat(),
			'is_own_message': True,
			'message_type': 'text'
		}
		MOCK_MESSAGES.append(message)
		
		# Generate AI response using Supermemory
		if int(room_id) == 1:  # Support chat
			time.sleep(0.3)
			
			# Try to use Supermemory for AI-powered response
			supermemory = get_supermemory_client()
			ai_response_content = None
			
			if supermemory:
				try:
					# Generate AI response with memory context
					chat_response = supermemory.chat_completion(
						messages=[
							{
								'role': 'system',
								'content': 'You are a helpful NMTSA LMS support assistant. Help users with course-related questions, enrollment, and general support.'
							},
							{
								'role': 'user',
								'content': content
							}
						],
						use_memory=True
					)
					
					if chat_response.get('success'):
						ai_response_content = chat_response.get('response')
						
						# Add this interaction to memory for future context
						supermemory.add_memory(
							content=f"User asked: {content}. Assistant responded: {ai_response_content}",
							metadata={
								'type': 'chat_interaction',
								'user_id': str(user_id),
								'room_id': str(room_id)
							}
						)
				except Exception as e:
					print(f"[Chat] Supermemory error: {e}")
					ai_response_content = None
			
			# Fallback to simple response if Supermemory unavailable
			if not ai_response_content:
				ai_response_content = 'Thanks for your message! An admin will respond shortly.'
			
			response_msg = {
				'id': len(MOCK_MESSAGES) + 101,
				'room_id': int(room_id),
				'content': ai_response_content,
				'sender': 'NMTSA Assistant',
				'sender_id': 999,
				'timestamp': timezone.now().isoformat(),
				'is_own_message': False,
				'message_type': 'text'
			}
			MOCK_MESSAGES.append(response_msg)
		
		return JsonResponse({
			'success': True,
			'message': message
		})
		
	except json.JSONDecodeError:
		return JsonResponse({
			'success': False,
			'error': 'Invalid request format'
		}, status=400)
	except Exception as e:
		return JsonResponse({
			'success': False,
			'error': 'An error occurred while sending the message'
		}, status=500)


@require_http_methods(["POST"])
def chat_update_typing(request, room_id):
	"""
	Update typing indicator status for current user.
	Available to all users (authenticated or not).
	"""
	try:
		session_user = request.session.get('user', {})
		user_id = session_user.get('user_id', 'guest')
		user_name = session_user.get('full_name', 'Guest')
		
		# Store typing status (expires after 3 seconds)
		key = f"{room_id}_{user_id}"
		MOCK_TYPING_USERS[key] = {
			'user_id': user_id,
			'user_name': user_name,
			'timestamp': timezone.now()
		}
		
		return JsonResponse({
			'success': True
		})
		
	except Exception as e:
		return JsonResponse({
			'success': False,
			'error': 'Failed to update typing status'
		}, status=500)


@require_http_methods(["GET"])
def chat_get_typing(request, room_id):
	"""
	Get list of users currently typing in a room.
	Available to all users (authenticated or not).
	"""
	session_user = request.session.get('user', {})
	current_user_id = session_user.get('user_id', 'guest')
	
	typing_users = []
	now = timezone.now()
	
	# Clean up old typing indicators and collect active ones
	expired_keys = []
	for key, data in MOCK_TYPING_USERS.items():
		if key.startswith(f"{room_id}_"):
			# Check if expired (more than 3 seconds old)
			if (now - data['timestamp']).total_seconds() > 3:
				expired_keys.append(key)
			elif data['user_id'] != current_user_id:
				typing_users.append(data['user_name'])
	
	# Remove expired entries
	for key in expired_keys:
		del MOCK_TYPING_USERS[key]
	
	return JsonResponse({
		'success': True,
		'typing_users': typing_users
	})


@require_http_methods(["POST"])
def search_courses_semantic(request):
	"""
	Search courses using Supermemory semantic search.
	Available to all users for course discovery.
	"""
	try:
		data = json.loads(request.body)
		query = data.get('query', '').strip()
		limit = data.get('limit', 10)
		
		if not query:
			return JsonResponse({
				'success': False,
				'error': 'Search query is required'
			}, status=400)
		
		# Try to use Supermemory for semantic search
		supermemory = get_supermemory_client()
		
		if supermemory:
			try:
				# Search for courses
				search_results = supermemory.search_courses(query, limit=limit)
				
				# Format results for frontend
				courses = []
				for result in search_results:
					courses.append({
						'id': result.get('id'),
						'title': result.get('title', result.get('content', '')[:100]),
						'description': result.get('content', ''),
						'relevance_score': result.get('score', 0),
						'metadata': result.get('metadata', {})
					})
				
				return JsonResponse({
					'success': True,
					'courses': courses,
					'total': len(courses)
				})
				
			except Exception as e:
				print(f"[Search] Supermemory error: {e}")
				# Fallback to empty results
				return JsonResponse({
					'success': True,
					'courses': [],
					'total': 0,
					'message': 'Search temporarily unavailable'
				})
		else:
			# Supermemory not configured - return empty results
			return JsonResponse({
				'success': True,
				'courses': [],
				'total': 0,
				'message': 'Semantic search not configured'
			})
			
	except json.JSONDecodeError:
		return JsonResponse({
			'success': False,
			'error': 'Invalid request format'
		}, status=400)
	except Exception as e:
		return JsonResponse({
			'success': False,
			'error': 'An error occurred during search'
		}, status=500)
