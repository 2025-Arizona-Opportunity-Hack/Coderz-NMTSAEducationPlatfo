# Supermemory AI Chat Integration - Complete Setup Guide

## Overview

The NMTSA LMS chatbot is powered by **Supermemory AI** with **Google Gemini**, providing intelligent, context-aware responses about courses and the platform. The chatbot:

- ✅ Focuses ONLY on NMTSA LMS website and neurologic music therapy courses
- ✅ Uses semantic memory to provide accurate course information
- ✅ Remembers conversation context for personalized responses
- ✅ Uses **Google Gemini** with **FREE tier** (60 requests/minute)
- ✅ Does NOT modify explore courses search functionality

## Architecture

### Components
1. **Supermemory SDK** - Memory management and semantic search
2. **Memory Router** - Automatically injects relevant memories into LLM context
3. **Google Gemini** - Natural language generation (FREE tier available)
4. **Course Memory** - Stores course data for semantic search

### How It Works
```
User Message 
    ↓
Memory Router searches relevant memories (courses, FAQs, past conversations)
    ↓
Google Gemini generates response with memory context
    ↓
Response restricted to NMTSA LMS domain via system prompt
    ↓
Conversation stored in memory for future context
```

## Installation

### 1. Install Required Packages

```bash
cd nmtsa_lms
pip install --pre supermemory openai
```

**Note**: The `openai` package is used for both OpenAI and Gemini (via compatible API).

### 2. Get API Keys

#### Google Gemini API Key (FREE Tier)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Get API Key" or "Create API Key"
4. Copy the key (starts with `AIza...`)

**Benefits:**
- ✅ FREE tier: 60 requests/minute
- ✅ Fast responses
- ✅ Good quality for chatbots
- ✅ No credit card required
- ✅ Easy setup

#### Supermemory API Key

1. Go to [Supermemory Dashboard](https://supermemory.ai/dashboard)
2. Sign up for free account
3. Navigate to API Keys section
4. Generate new API key
5. Copy the key

### 3. Configure Environment Variables

Create or update `.env` file in project root:

```bash
# Supermemory Configuration (Required)
SUPERMEMORY_API_KEY=your_supermemory_api_key_here

# Google Gemini Configuration (Required)
GEMINI_API_KEY=AIza...your_gemini_key_here
```

## Setup and Seeding

### 1. Seed Website Information

This adds general platform information to memory:

```bash
cd nmtsa_lms
python manage.py seed_website_memory
```

**What it adds:**
- Platform features and capabilities
- User roles (student/teacher/admin)
- Course structure and enrollment process
- Getting started guide
- FAQ information

### 2. Sync Existing Courses

This indexes all published courses for semantic search:

```bash
# Sync only published and approved courses
python manage.py sync_courses_to_memory

# Or sync ALL courses including unpublished
python manage.py sync_courses_to_memory --all

# Or sync a specific course
python manage.py sync_courses_to_memory --course-id 5
```

**What it does:**
- Extracts course title, description, tags, modules
- Creates rich semantic content
- Uses `custom_id` for idempotent updates (no duplicates)
- Stores in `nmtsa-courses` container tag

### 3. Test the Setup

Run Django development server:

```bash
python manage.py runserver
```

Open the chat widget and test:
- "What courses are available?"
- "Tell me about music therapy courses"
- "How do I enroll in a course?"
- "What are the platform features?"

## Course Memory Integration

### Automatic Syncing

Courses are automatically synced to memory when:
- ✅ Teacher creates a new course (after admin approval)
- ✅ Course is published
- ✅ Course content is updated

### Manual Syncing

If you need to re-sync courses:

```bash
# Re-sync all published courses
python manage.py sync_courses_to_memory

# Force sync including drafts
python manage.py sync_courses_to_memory --all
```

### How It Works

When you add/update a course, the system:
1. Extracts course data (title, description, tags, modules)
2. Formats as semantic-friendly text
3. Calls `add_course_to_memory()` with `custom_id=course-{id}`
4. Supermemory updates existing memory if custom_id exists (no duplicates)
5. Course becomes searchable in chat and explore pages

## Chat Functionality

### Domain Restriction

The chatbot is restricted to NMTSA LMS topics via system prompt:

**Will answer:**
- ✅ Course recommendations and details
- ✅ Platform features and navigation
- ✅ Enrollment process
- ✅ Teacher verification
- ✅ Student progress tracking
- ✅ Payment and pricing

**Will NOT answer:**
- ❌ General music therapy questions (redirects to appropriate resources)
- ❌ Off-topic questions
- ❌ Medical advice
- ❌ Unrelated topics

### Memory Context

Each conversation:
1. User message triggers Memory Router
2. Router searches for relevant memories (courses, FAQs, past conversations)
3. Top relevant memories injected into LLM context
4. LLM generates response with full context
5. Interaction stored in memory with user-specific tag

## Explore Courses Search

**IMPORTANT**: The explore courses search functionality is **UNCHANGED**.

- Uses same `search_courses()` method
- Semantic search via Supermemory
- Returns courses with relevance scores
- Works independently of chat

The integration only adds/improves:
- Chat responses with memory context
- Automatic course indexing
- Better semantic matching

## API Endpoints

### Chat Endpoints (Unchanged)
- `GET /lms/api/chat/rooms/` - List chat rooms
- `GET /lms/api/chat/rooms/<id>/messages/` - Get messages
- `POST /lms/api/chat/rooms/<id>/send/` - Send message (triggers AI)
- `POST /lms/api/chat/rooms/<id>/typing/` - Update typing status
- `GET /lms/api/chat/rooms/<id>/typing/status/` - Get typing status

### Search Endpoint (Unchanged)
- `POST /lms/api/courses/search/` - Semantic course search

## Configuration Options

### Environment Variables

```bash
# Required
SUPERMEMORY_API_KEY=your_supermemory_key_here
GEMINI_API_KEY=your_gemini_key_here
```

### Django Settings

In `nmtsa_lms/settings.py`:

```python
# Supermemory AI Configuration
SUPERMEMORY_API_KEY = os.getenv('SUPERMEMORY_API_KEY', '')

# Google Gemini Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
```

## Troubleshooting

### "Supermemory not configured" error

**Solution**: Ensure API keys are set in `.env` file and file is in project root.

### Chat not responding

1. Check API keys are valid
2. Check Django console for errors
3. Verify packages installed: `pip list | grep -E "supermemory|openai"`
4. Test API connection:
```python
from lms.supermemory_client import get_supermemory_client
client = get_supermemory_client()
print(client)  # Should not be None
```

### Course search not working

1. Run sync command: `python manage.py sync_courses_to_memory`
2. Check if courses are published and approved
3. Verify Supermemory API key is set

### "Import openai could not be resolved"

**Solution**: Install package: `pip install openai`

### Rate limit errors (Gemini)

**Solution**: Free tier has 60 requests/minute. Either:
- Wait a minute between tests
- Upgrade to paid tier
- Switch to OpenAI provider

## Cost Considerations

### Google Gemini
- **Free Tier**: 60 requests/minute ✅
- **Cost**: $0.00 for most use cases
- **Perfect for**: Development, production, all deployments
- **Get Key**: https://makersuite.google.com/app/apikey

### Supermemory
- **Free Tier**: Yes (generous limits)
- **Cost**: Check [Supermemory Pricing](https://supermemory.ai/pricing)
- **Best for**: Most applications fit in free tier

## Security Best Practices

1. ✅ Never commit `.env` file to git
2. ✅ Use environment variables for all API keys
3. ✅ Rotate API keys periodically
4. ✅ Set appropriate rate limits in production
5. ✅ Monitor API usage and costs

## Production Deployment

### Before Deploying

1. Set all environment variables in hosting platform
2. Run database migrations: `python manage.py migrate`
3. Seed website info: `python manage.py seed_website_memory`
4. Sync courses: `python manage.py sync_courses_to_memory`
5. Test chat functionality
6. Monitor API usage and costs

### Recommended Settings

```bash
# Production .env
DEBUG=False
SUPERMEMORY_API_KEY=prod_key_here
GEMINI_API_KEY=prod_gemini_key_here
```

## Maintenance

### Regular Tasks

1. **Weekly**: Review chat logs for quality
2. **Monthly**: Check API usage and costs
3. **When adding courses**: Sync automatically happens, but verify
4. **After bulk updates**: Run `sync_courses_to_memory --all`

### Monitoring

Check Django logs for:
- `[Chat] Supermemory error:` - API issues
- `[Search] Supermemory error:` - Search issues
- `Chat completion successful` - Working correctly

## Support

For issues:
1. Check this documentation
2. Review Django console errors
3. Check [Supermemory Docs](https://supermemory.ai/docs)
4. Check [Gemini API Docs](https://ai.google.dev/docs)
5. Create issue in project repository

## Summary

✅ **Installation**: `pip install --pre supermemory openai`
✅ **API Keys**: Get Supermemory + Gemini (or OpenAI) keys
✅ **Configuration**: Set in `.env` file
✅ **Seeding**: Run `seed_website_memory` and `sync_courses_to_memory`
✅ **Testing**: Open chat and ask about courses
✅ **Explore Search**: Unchanged, works as before

The chatbot now intelligently answers questions about NMTSA LMS and courses, powered by Supermemory's memory-enhanced AI!
