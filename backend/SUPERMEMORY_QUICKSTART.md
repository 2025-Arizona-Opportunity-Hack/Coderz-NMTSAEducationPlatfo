# Supermemory Integration - Quick Start Guide

## Overview

Supermemory has been integrated into the NMTSA LMS backend using the official Python SDK to provide:
1. **AI-powered chat assistant** - Contextual responses based on user queries
2. **Contextual course search** - Natural language course discovery
3. **Personalized recommendations** - Course suggestions based on interests

## Files Created

### Backend Core
- **`nmtsa_lms/supermemory_client.py`** - Simple Supermemory client singleton using official SDK
- **`nmtsa_lms/settings.py`** - Added SUPERMEMORY configuration (lines added at end)

### Chat Enhancement
- **`student_dash/chat_views.py`** - Modified to use Supermemory for intelligent responses
  - Changed permissions from `IsAuthenticated` to `AllowAny`
  - Process messages with contextual AI
  - Store user queries as memories

### New Search Features
- **`student_dash/search_views.py`** - NEW file with 2 endpoints:
  - `contextual_course_search()` - POST natural language search
  - `get_course_recommendations()` - GET personalized recommendations
- **`student_dash/search_urls.py`** - NEW file with URL routing

### URL Configuration
- **`nmtsa_lms/urls.py`** - Added search endpoint: `path('api/v1/search/', include('student_dash.search_urls'))`

### Documentation
- **`SUPERMEMORY_INTEGRATION.md`** - Comprehensive integration guide
- **`.env.supermemory`** - Environment variable template
- **`requirements.txt`** - Updated with requests dependency

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install supermemory
# or using uv
uv add supermemory
```

### 2. Get Supermemory API Key

1. Visit [https://supermemory.ai](https://supermemory.ai)
2. Sign up for a free account
3. Create a new project in your dashboard
4. Copy your API key

### 3. Configure Environment

Add to your `.env` file (create one if it doesn't exist):

```env
SUPERMEMORY_API_KEY=your_api_key_here
SUPERMEMORY_BASE_URL=https://api.supermemory.ai
SUPERMEMORY_PROJECT_ID=  # Optional
```

**NOTE**: If you don't set the API key, everything will still work with basic functionality (no AI enhancement).

### 4. Restart Django Server

```bash
cd backend/nmtsa_lms
python manage.py runserver
```

## API Endpoints

### Chat with AI Assistant

**Endpoint**: `POST /api/v1/chat/messages`

**Body**:
```json
{
  "content": "What courses do you offer for beginners?",
  "conversationId": "conversation-uuid"
}
```

**Response**:
```json
{
  "userMessage": {
    "id": "uuid-1",
    "content": "What courses do you offer for beginners?",
    "senderId": "guest",
    "timestamp": "2025-10-11T10:00:00Z"
  },
  "assistantMessage": {
    "id": "uuid-2",
    "content": "We offer a variety of beginner courses...",
    "senderId": "assistant",
    "timestamp": "2025-10-11T10:00:01Z"
  }
}
```

### Contextual Course Search

**Endpoint**: `POST /api/v1/search/courses/contextual/`

**Body**:
```json
{
  "query": "courses about music therapy for children with autism"
}
```

**Response**:
```json
{
  "query": "courses about music therapy for children with autism",
  "count": 5,
  "ai_enhanced": true,
  "courses": [
    {
      "id": "1",
      "title": "Pediatric Music Therapy Basics",
      "description": "Introduction to music therapy techniques...",
      "published_by": {
        "id": "2",
        "full_name": "Dr. Jane Smith"
      },
      "tags": ["children", "autism", "therapy"]
    }
  ]
}
```

### Get Course Recommendations

**Endpoint**: `GET /api/v1/search/courses/recommendations/`

**Query Parameters**:
- `interests` - Comma-separated interests (e.g., "music therapy,children")
- `limit` - Number of results (default: 5)

**Example**:
```
GET /api/v1/search/courses/recommendations/?interests=music%20therapy,children&limit=5
```

**Response**:
```json
{
  "interests": "music therapy,children",
  "count": 5,
  "courses": [...]
}
```

## Testing

### Test Chat (using curl)

```bash
curl -X POST http://localhost:8000/api/v1/chat/messages \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Tell me about your music therapy courses",
    "conversationId": "test-conversation-1"
  }'
```

### Test Contextual Search

```bash
curl -X POST http://localhost:8000/api/v1/search/courses/contextual/ \
  -H "Content-Type: application/json" \
  -d '{"query": "beginner friendly courses about rhythm therapy"}'
```

### Test Recommendations

```bash
curl http://localhost:8000/api/v1/search/courses/recommendations/?interests=music%20therapy&limit=3
```

## How It Works

### Chat Intelligence Flow

1. User sends message
2. Supermemory searches existing memories for context
3. Stores user query as new memory
4. Generates contextual response
5. Returns both user message and AI response

### Search Enhancement Flow

1. User enters natural language query
2. Basic Django ORM keyword search
3. Supermemory expands search with related keywords from memories
4. Stores search query for future learning
5. Returns ranked courses with AI-enhanced results

### Graceful Degradation

If Supermemory is not configured:
- Chat returns helpful default responses
- Search uses standard keyword matching
- No errors or failures
- Seamless user experience

## Frontend Integration

### Chat Component (Already Done)

The chat component in `frontend/src/components/chat/Chat.tsx` automatically works with the enhanced backend.

### Add Contextual Search (Optional Enhancement)

You can add a search input in the course catalog that calls the contextual search endpoint:

```typescript
import { chatService } from '../../services/chat.service';

// In your course search component
const handleContextualSearch = async (query: string) => {
  const response = await axios.post('/api/v1/search/courses/contextual/', {
    query
  });
  setCourses(response.data.courses);
};
```

## Configuration Options

### Environment Variables

```env
# Required for AI features
SUPERMEMORY_API_KEY=sk_your_api_key

# Optional: Custom endpoint (for self-hosted)
SUPERMEMORY_BASE_URL=https://api.supermemory.ai

# Optional: Scope memories to project
SUPERMEMORY_PROJECT_ID=project_abc123
```

### Client Configuration

Edit `nmtsa_lms/supermemory_client.py` to customize:
- API timeout
- Retry logic
- Default memory limits
- Error handling

## Monitoring

### Check Integration Status

```python
# In Django shell
python manage.py shell

from nmtsa_lms.supermemory_client import get_supermemory_client

client = get_supermemory_client()
if client:
    print("✓ Supermemory configured")
    # Try a test search
    response = client.search.execute(q="test")
    print(f"✓ API working - {len(response.results)} results")
else:
    print("✗ Supermemory not configured (API key missing)")
```

### View Memories

Visit your Supermemory dashboard at [https://supermemory.ai/dashboard](https://supermemory.ai/dashboard) to:
- See stored memories
- Analyze search patterns
- Review API usage
- Manage projects

## Troubleshooting

### Chat not using AI

**Problem**: Chat returns basic responses even with API key set

**Solution**:
1. Check `.env` file has `SUPERMEMORY_API_KEY=...`
2. Restart Django server
3. Check console for error messages
4. Verify API key is valid in Supermemory dashboard

### Search not finding courses

**Problem**: Contextual search returns empty results

**Solution**:
1. Make sure courses exist in database with `is_published=True` and `admin_approved=True`
2. Initial setup may have no memories - add seed data
3. Try basic keyword search first to verify courses exist
4. Check Django logs for query errors

### API Rate Limits

**Problem**: Getting rate limit errors from Supermemory

**Solution**:
1. Implement caching for frequent queries
2. Reduce memory storage frequency
3. Use pagination for large searches
4. Upgrade Supermemory plan if needed

## Next Steps

### Enhance with More Context

Add course data to Supermemory for better recommendations:

```python
from nmtsa_lms.supermemory_client import get_supermemory_client
from teacher_dash.models import Course

client = get_supermemory_client()
if client:
    for course in Course.objects.filter(is_published=True):
        # Add course information as memory
        client.memories.add(
            content=f"Course: {course.title}. {course.description}"
        )
```

### Add User Preferences

When authentication is re-enabled, store user-specific memories:

```python
client.memories.add(
    content=f"User {user.id} is interested in: {interests}"
)
```

### Implement WebSocket Updates

For real-time chat with typing indicators and instant responses.

## Resources

- [Supermemory Documentation](https://docs.supermemory.ai)
- [API Reference](https://api.supermemory.ai/docs)
- [Integration Guide](./SUPERMEMORY_INTEGRATION.md) - Detailed technical doc
- [GitHub Repository](https://github.com/supermemoryai/supermemory)

## Support

For issues with:
- **Supermemory API**: [support@supermemory.ai](mailto:support@supermemory.ai)
- **NMTSA LMS Integration**: Check the detailed `SUPERMEMORY_INTEGRATION.md` file
- **General Django Help**: Django documentation

---

**Status**: ✅ Integration Complete
**Requires**: Supermemory API key (free tier available)
**Impact**: Enhanced chat and search without breaking existing functionality
