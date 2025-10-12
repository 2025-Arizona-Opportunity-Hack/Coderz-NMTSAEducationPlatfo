# NMTSA LMS Chat System with Supermemory AI - Implementation Guide

## Overview
A fully-functional chat system with AI-powered responses using Supermemory for memory-enhanced context and semantic search capabilities.

## Features Implemented

### 1. **Chat Interface** ✅
- **Always visible** floating chat button (bottom-right)
- **Dialog-style** chat window with professional design
- **Available to all users** (authenticated or not)
- **Autism-friendly**: No animations, clear visuals, high contrast support
- **Mobile responsive**: Adapts to all screen sizes

### 2. **Backend APIs** ✅
- **Message Management**: Send/receive messages with mock data
- **Typing Indicators**: Real-time typing status
- **Room Management**: Support chat, group chats (extensible)
- **AI Responses**: Automated responses using Supermemory

### 3. **Supermemory Integration** ✅
- **Chat Completion**: AI-powered responses with memory context
- **Memory Storage**: Automatic conversation history storage
- **Semantic Search**: Find courses using natural language
- **Course Indexing**: Automatically index courses for search

## File Structure

```
nmtsa_lms/
├── lms/
│   ├── views.py                    # Chat & search API endpoints
│   ├── supermemory_client.py       # Supermemory integration
│   ├── course_memory.py            # Course indexing utilities
│   ├── models.py                   # ChatRoom & ChatMessage models
│   └── urls.py                     # API routes
├── nmtsa_lms/
│   ├── static/js/chat.js           # Frontend chat manager
│   └── templates/
│       ├── base.html               # Includes chat component
│       └── components/chat.html    # Chat UI template
└── .env                            # Supermemory configuration
```

## Setup Instructions

### 1. Install Supermemory SDK

```bash
pip install --pre supermemory
```

The `--pre` flag is required because the SDK is in pre-release.

### 2. Configure Environment Variables

Add to your `.env` file (copy from `nmtsa_lms/.env.example`):

```bash
# Supermemory Configuration
SUPERMEMORY_API_KEY=your-supermemory-api-key-here

# Optional: OpenAI API Key (for production chat completions)
OPENAI_API_KEY=your-openai-api-key-here
```

Get your Supermemory API key from: https://console.supermemory.ai/

### 3. Run Migrations

```bash
cd nmtsa_lms
python manage.py makemigrations lms
python manage.py migrate
```

### 4. Start Server

```bash
python manage.py runserver
```

### 5. Test the Chat

1. Open any page (e.g., `http://localhost:8000/`)
2. Look for the **purple gradient chat button** in bottom-right
3. Click to open chat dialog
4. Type a message and press Send
5. AI assistant will respond automatically

## API Endpoints

### Chat APIs

```http
GET  /lms/api/chat/rooms/
# Returns list of available chat rooms

GET  /lms/api/chat/rooms/1/messages/
# Get message history for room 1

POST /lms/api/chat/rooms/1/send/
{
  "content": "Hello, I need help with courses"
}
# Send message and receive AI response

POST /lms/api/chat/rooms/1/typing/
# Update typing indicator

GET  /lms/api/chat/rooms/1/typing/status/
# Get list of users currently typing
```

### Course Search API

```http
POST /lms/api/courses/search/
{
  "query": "autism music therapy",
  "limit": 10
}
# Semantic search for courses using Supermemory
```

## Using Supermemory

### In Chat (Automatic)

When a user sends a message:
1. Message is sent to backend
2. Backend calls Supermemory chat completion
3. Supermemory searches relevant memories
4. AI generates contextual response
5. Interaction is saved to memory
6. Response sent back to user

### In Code (Manual)

```python
from lms.supermemory_client import get_supermemory_client

# Get client instance
supermemory = get_supermemory_client()

# Generate AI response
response = supermemory.chat_completion(
    messages=[
        {'role': 'system', 'content': 'You are a helpful assistant'},
        {'role': 'user', 'content': 'What courses are available?'}
    ],
    use_memory=True  # Use memory context
)

# Add to memory
supermemory.add_memory(
    content="User prefers morning classes",
    metadata={'type': 'preference', 'user_id': 123}
)

# Search memories
results = supermemory.search_memories(
    query="user preferences",
    limit=5
)

# Search courses semantically
courses = supermemory.search_courses(
    query="beginner music therapy",
    limit=10
)
```

### Adding Courses to Memory

```python
from lms.course_memory import add_course_to_memory

# When creating a course
course = Course.objects.create(
    title="NMT Fundamentals",
    description="Introduction to Neurologic Music Therapy",
    # ... other fields
)

# Index in Supermemory
add_course_to_memory({
    'id': course.id,
    'title': course.title,
    'description': course.description,
    'tags': list(course.tags.names()),
    'modules': [{'title': m.title} for m in course.modules.all()],
    'is_paid': course.is_paid,
    'is_published': course.is_published
})
```

## Frontend Usage

The chat is automatically available on all pages via `base.html`. To customize:

```javascript
// Access chat manager globally
window.chatManager.openChat();      // Open chat
window.chatManager.closeChat();     // Close chat
window.chatManager.sendMessage();   // Send current message
window.chatManager.loadMessages();  // Refresh messages
```

## Customization

### Change Chat Appearance

Edit `templates/components/chat.html`:

```html
<!-- Change chat button color -->
<style>
  .chat-toggle-button {
    background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
  }
</style>
```

### Add New Chat Rooms

In `views.py` - `chat_get_rooms()`:

```python
mock_rooms = [
    {
        'id': 1,
        'name': 'Support Chat',
        'room_type': 'support',
        # ...
    },
    {
        'id': 3,  # Add new room
        'name': 'Billing Support',
        'room_type': 'support',
        # ...
    }
]
```

### Customize AI Behavior

In `supermemory_client.py` - `chat_completion()`:

```python
# Change system message
enhanced_messages.insert(0, {
    'role': 'system',
    'content': 'Your custom AI personality here...'
})
```

## Troubleshooting

### Chat button not appearing
- Check browser console for JavaScript errors
- Ensure `chat.js` is loaded: View page source and search for `chat.js`
- Verify `templates/components/chat.html` is included in `base.html`

### AI not responding
- Check Supermemory API key in `.env`
- View server console for error messages
- Test Supermemory client directly:
  ```python
  from lms.supermemory_client import get_supermemory_client
  client = get_supermemory_client()
  print(client)  # Should not be None
  ```

### CSRF token errors
- Ensure `getCSRFToken()` method works in `chat.js`
- Check cookies in browser DevTools
- Verify Django CSRF middleware is enabled

### Course search not working
- Courses must be indexed in Supermemory first
- Run indexing for existing courses:
  ```python
  from teacher_dash.models import Course
  from lms.course_memory import add_course_to_memory
  
  for course in Course.objects.filter(is_published=True):
      add_course_to_memory({
          'id': course.id,
          'title': course.title,
          'description': course.description,
          'tags': list(course.tags.names()),
          # ...
      })
  ```

## Production Considerations

### 1. Replace Mock Data
- Implement real database queries using `ChatRoom` and `ChatMessage` models
- Store messages in database instead of `MOCK_MESSAGES` list

### 2. Add WebSocket Support
- Use Django Channels for real-time messaging
- Replace HTTP polling with WebSocket connections

### 3. Rate Limiting
- Add rate limiting to prevent API abuse
- Use Django-ratelimit or similar

### 4. Authentication
- Enforce authentication for sensitive operations
- Add `@login_required` decorator to relevant views

### 5. Monitoring
- Log all Supermemory API calls
- Monitor response times and errors
- Set up alerts for failures

### 6. Caching
- Cache frequent Supermemory searches
- Use Redis for typing indicators instead of memory

## Next Steps

1. **Integrate Real OpenAI**: Replace mock responses with actual OpenAI API
2. **Add File Upload**: Allow users to share documents in chat
3. **Voice Messages**: Add audio recording capabilities
4. **Rich Media**: Support images, videos, embeds
5. **Notifications**: Browser notifications for new messages
6. **Mobile App**: React Native/Flutter app with same APIs
7. **Analytics**: Track chat usage and popular queries
8. **Multi-language**: Support multiple languages with i18n

## Support

For issues or questions:
1. Check server logs: `nmtsa_lms/` directory
2. Check browser console: F12 → Console tab
3. Review API responses: Network tab in DevTools
4. Test Supermemory directly: Use their dashboard/API tester

## Credits

- **Supermemory**: Memory-enhanced AI capabilities
- **Django**: Backend framework
- **Tailwind CSS**: Styling system
- **Vanilla JavaScript**: No dependencies, pure performance
