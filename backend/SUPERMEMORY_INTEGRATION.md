# Supermemory Integration for NMTSA LMS

This document explains how Supermemory is integrated into the NMTSA LMS backend for AI-powered chat and contextual course search.

## Features

### 1. **AI-Powered Chat Bot** (`chat_views.py`)
The chat interface uses the official Supermemory SDK to provide intelligent, context-aware responses:

- **Simple Integration**: Uses `client.search.execute()` and `client.memories.add()`
- **Memory Storage**: User queries stored with `client.memories.add()`
- **Contextual Responses**: Search with `client.search.execute(q=query)`
- **Smart Fallbacks**: Default helpful responses when Supermemory is unavailable
- **No Authentication Required**: Public access for information bot functionality

### 2. **Contextual Course Search** (`search_views.py`)
AI-enhanced course discovery using natural language:

- **POST `/api/v1/search/courses/contextual/`**: 
  - Natural language course search
  - Example: `{"query": "courses about music therapy for children"}`
  - Supermemory expands search with contextual keywords
  
- **GET `/api/v1/search/courses/recommendations/?interests=music therapy,children`**:
  - Personalized course recommendations
  - Based on user interests and past searches
  - Falls back to popular courses if no interests provided

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install supermemory
# or using uv
uv add supermemory
```

### 2. Get Supermemory API Key

1. Sign up at [https://supermemory.ai](https://supermemory.ai)
2. Create a project and get your API key
3. Optionally get your project ID for scoped memories

### 3. Configure Environment Variables

Add to your `.env` file:

```env
SUPERMEMORY_API_KEY=your_api_key_here
SUPERMEMORY_BASE_URL=https://api.supermemory.ai
SUPERMEMORY_PROJECT_ID=your_project_id  # Optional
```

### 4. Test the Integration

**Test Chat:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Tell me about music therapy courses", "conversationId": "test-123"}'
```

**Test Contextual Search:**
```bash
curl -X POST http://localhost:8000/api/v1/search/courses/contextual/ \
  -H "Content-Type: application/json" \
  -d '{"query": "beginner courses about music therapy for children"}'
```

**Test Recommendations:**
```bash
curl http://localhost:8000/api/v1/search/courses/recommendations/?interests=music%20therapy,children&limit=5
```

## Architecture

### Files Created/Modified

1. **`nmtsa_lms/supermemory_client.py`** - Supermemory API client
   - `SupermemoryClient` class with methods:
     - `add_memory()` - Store information
     - `search_memories()` - Query stored knowledge
     - `fetch_memory()` - Retrieve specific memory
   - Singleton pattern with `get_supermemory_client()`

2. **`student_dash/chat_views.py`** - Enhanced chat with AI
   - Changed permissions from `IsAuthenticated` to `AllowAny`
   - Process messages with Supermemory for contextual responses
   - Store user queries as memories
   - Smart fallback responses for common questions

3. **`student_dash/search_views.py`** - New AI search endpoints
   - Contextual course search with memory-enhanced keywords
   - Personalized recommendations based on interests
   - Stores search queries for learning user preferences

4. **`student_dash/search_urls.py`** - URL routing for search
   - `/api/v1/search/courses/contextual/` - POST contextual search
   - `/api/v1/search/courses/recommendations/` - GET recommendations

5. **`nmtsa_lms/settings.py`** - Configuration
   - Added Supermemory environment variables
   - API key, base URL, and project ID settings

6. **`nmtsa_lms/urls.py`** - Main URL config
   - Added `path('api/v1/search/', include('student_dash.search_urls'))`

## How It Works

### Chat Message Flow

1. User sends message via POST `/api/v1/chat/messages`
2. Backend stores user message
3. **Supermemory Integration**:
   - Search existing memories for relevant context
   - Store user's query as new memory
   - Generate contextual AI response
4. Return both user message and AI response

### Course Search Flow

1. User enters natural language query (e.g., "courses for beginners about rhythm")
2. Basic keyword search on Course model (title, description, tags)
3. **Supermemory Enhancement**:
   - Search memories for related course recommendations
   - Extract additional keywords from memory context
   - Expand search query with AI-derived keywords
   - Store search for future recommendations
4. Return ranked course results

### Graceful Degradation

- If `SUPERMEMORY_API_KEY` is not set, features work with basic functionality
- Chat returns helpful default responses
- Search uses standard Django ORM queries
- No errors thrown, seamless fallback

## Example Responses

### Chat Response
```json
{
  "userMessage": {
    "id": "uuid-1",
    "content": "What courses do you offer?",
    "senderId": "guest",
    "timestamp": "2025-10-11T10:00:00Z"
  },
  "assistantMessage": {
    "id": "uuid-2",
    "content": "We offer a variety of music therapy courses! You can browse our catalog...",
    "senderId": "assistant",
    "timestamp": "2025-10-11T10:00:01Z"
  }
}
```

### Contextual Search Response
```json
{
  "query": "courses about music therapy for children",
  "count": 5,
  "ai_enhanced": true,
  "courses": [
    {
      "id": "1",
      "title": "Pediatric Music Therapy Basics",
      "description": "Introduction to music therapy techniques for children...",
      "tags": ["children", "beginners", "therapy"]
    }
  ]
}
```

## Best Practices

1. **API Key Security**: Never commit `.env` file with real API keys
2. **Rate Limiting**: Supermemory has rate limits, implement caching if needed
3. **Memory Management**: Regularly review and clean old memories via Supermemory dashboard
4. **Context Building**: Add more course data to memories during initial setup
5. **Error Handling**: Always provide fallback behavior when Supermemory is unavailable

## Future Enhancements

- **WebSocket Integration**: Real-time typing indicators with Supermemory context
- **User Profiles**: Personalized memories per authenticated user (when auth is re-enabled)
- **Course Content Indexing**: Automatically add course details to Supermemory
- **Multi-language Support**: Translate queries and responses
- **Analytics**: Track search patterns and improve recommendations

## Troubleshooting

**Chat not responding intelligently:**
- Check `SUPERMEMORY_API_KEY` is set correctly
- Verify API key has proper permissions
- Check console logs for API errors

**Search returning too few results:**
- Initial setup may have no memories yet
- Add seed data to Supermemory (course descriptions, FAQs)
- Adjust `limit` parameter in searches

**API rate limits:**
- Implement Redis caching for frequent queries
- Batch memory additions
- Use pagination for large result sets

## Additional Resources

- [Supermemory Documentation](https://docs.supermemory.ai)
- [Supermemory Python SDK](https://github.com/supermemoryai/supermemory)
- [API Reference](https://api.supermemory.ai/docs)
