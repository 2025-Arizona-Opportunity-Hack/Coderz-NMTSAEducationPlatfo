# Supermemory Chat - Quick Reference

## 🚀 Quick Start (5 Minutes)

### 1. Install Packages
```bash
pip install --pre supermemory openai
```

### 2. Get API Keys
- **Supermemory**: https://supermemory.ai/dashboard
- **Gemini** (FREE): https://makersuite.google.com/app/apikey

### 3. Set Environment Variables
```bash
# In .env file
SUPERMEMORY_API_KEY=your_supermemory_key
GEMINI_API_KEY=your_gemini_key
```

### 4. Seed Data
```bash
python manage.py seed_website_memory
python manage.py sync_courses_to_memory
```

### 5. Test
```bash
python manage.py runserver
# Open chat widget and ask: "What courses are available?"
```

## 📋 Key Commands

```bash
# Seed website info (run once)
python manage.py seed_website_memory

# Sync all published courses
python manage.py sync_courses_to_memory

# Sync specific course
python manage.py sync_courses_to_memory --course-id 5

# Sync everything including unpublished
python manage.py sync_courses_to_memory --all
```

## 🔑 Environment Variables

```bash
# Required
SUPERMEMORY_API_KEY=xxx
GEMINI_API_KEY=xxx           # FREE tier (60 req/min)
```

## 🎯 What Chatbot Answers

✅ **Answers:**
- Course recommendations
- Platform features
- How to enroll
- Teacher verification
- Student progress
- Pricing info

❌ **Does NOT answer:**
- Off-topic questions
- General medical advice
- Non-NMTSA topics

## 🔍 Important Notes

1. **Explore Courses Search**: UNCHANGED - still works the same
2. **Course Auto-Sync**: Happens when courses are published
3. **Memory Context**: Chatbot remembers conversation history
4. **Domain Restriction**: System prompt keeps bot on-topic

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Supermemory not configured" | Check `.env` has API keys |
| Chat not responding | Verify API keys valid, check console |
| Courses not found | Run `sync_courses_to_memory` |
| Rate limit error (Gemini) | Wait 1 minute or upgrade |
| Import errors | Run `pip install --pre supermemory openai` |

## 💰 Cost

| Service | Free Tier | Cost | Best For |
|---------|-----------|------|----------|
| **Gemini** | 60 req/min | $0.00 | Everything! ✅ |
| **Supermemory** | Generous | Free/Paid | All use cases |

**Total Cost**: $0.00 for most applications!

## 📚 Full Documentation

See `SUPERMEMORY_SETUP_GUIDE.md` for complete details.

## 🧪 Test Memory System

```python
# In Django shell
from lms.supermemory_client import get_supermemory_client

client = get_supermemory_client()
print(client)  # Should show client object

# Test chat
response = client.chat_completion(
    messages=[{"role": "user", "content": "What courses do you offer?"}]
)
print(response['response'])
```

## 🎓 Example Queries

Good questions to test:
- "What neurologic music therapy courses are available?"
- "How do I enroll in a course?"
- "What are the platform features?"
- "Tell me about the teacher verification process"
- "How does student progress tracking work?"

## ⚙️ Files Modified

- `lms/supermemory_client.py` - Main client with Gemini/OpenAI support
- `lms/course_memory.py` - Course indexing with custom_id
- `lms/views.py` - Chat endpoint using Memory Router
- `settings.py` - LLM provider configuration
- `requirements.txt` - Added `openai` package

## ✅ Checklist

- [ ] Installed packages
- [ ] Got Supermemory API key
- [ ] Got Gemini or OpenAI API key
- [ ] Set environment variables
- [ ] Ran seed_website_memory
- [ ] Ran sync_courses_to_memory
- [ ] Tested chat
- [ ] Verified explore courses still works
