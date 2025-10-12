# Chat System - Setup Checklist

## ✅ Completed

- [x] Created ChatRoom and ChatMessage models
- [x] Implemented 6 backend API endpoints
- [x] Built ChatManager JavaScript class (modular, ~600 lines)
- [x] Created dialog-style chat UI component
- [x] Made chat accessible to all users (no auth required)
- [x] Integrated Supermemory client for AI responses
- [x] Added semantic course search endpoint
- [x] Created course memory sync utilities
- [x] Updated copilot instructions with chat documentation
- [x] Created comprehensive implementation guide

## 🔲 Pending Setup (Required to Test)

### 1. Install Supermemory SDK
```bash
pip install --pre supermemory
```

### 2. Database Migrations
```bash
cd nmtsa_lms
python manage.py makemigrations lms
python manage.py migrate
```

### 3. Environment Configuration
Add to your `.env` file (copy from `.env.example`):
```bash
SUPERMEMORY_API_KEY=your-api-key-here
```
Get your API key from: https://console.supermemory.ai/

### 4. Test the Chat
```bash
python manage.py runserver
# Open http://localhost:8000/
# Look for purple chat button in bottom-right
```

## 🎯 Optional Enhancements

### Integrate Course Memory Sync
**Location**: `teacher_dash/views.py`

Add to course create/update views:
```python
from lms.course_memory import add_course_to_memory

# After course.save()
add_course_to_memory({
    'id': course.id,
    'title': course.title,
    'description': course.description,
    'tags': list(course.tags.names()),
    'modules': [{'title': m.title} for m in course.modules.all()],
})
```

### Index Existing Courses
Run this in Django shell to index all published courses:
```python
from teacher_dash.models import Course
from lms.course_memory import add_course_to_memory

for course in Course.objects.filter(is_published=True):
    add_course_to_memory({
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'tags': list(course.tags.names()),
        'modules': [{'title': m.title} for m in course.modules.all()],
    })
    print(f"Indexed: {course.title}")
```

### Replace Mock Data with Real Database
**Location**: `lms/views.py`

Currently uses `MOCK_MESSAGES` - replace with:
```python
messages = ChatMessage.objects.filter(room_id=room_id).order_by('created_at')
```

## 📊 Testing Checklist

- [ ] Chat button visible on landing page
- [ ] Chat button visible on authenticated pages (dashboard)
- [ ] Chat window opens on button click
- [ ] Can type and send messages
- [ ] AI responds to messages (requires Supermemory API key)
- [ ] Typing indicator works
- [ ] Chat persists state (open/closed) across page refreshes
- [ ] Mobile responsive (test on small screen)
- [ ] Theme system compatible (test all 4 themes)
- [ ] Semantic course search works (POST to `/lms/api/courses/search/`)

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Chat button not visible | Check browser console, ensure `chat.js` loaded |
| CSRF token errors | Clear cookies, refresh page |
| AI not responding | Check Supermemory API key in `.env` |
| Migration errors | Run `makemigrations` first, then `migrate` |
| Import errors | Ensure Django is running, not just linting |

## 📁 Key Files Reference

| File | Purpose |
|------|---------|
| `lms/views.py` | Chat API endpoints + Supermemory integration |
| `lms/supermemory_client.py` | Supermemory client singleton |
| `lms/course_memory.py` | Course indexing utilities |
| `static/js/chat.js` | Frontend chat manager |
| `templates/components/chat.html` | Chat UI component |
| `lms/models.py` | ChatRoom & ChatMessage models |
| `.env.example` | Environment variable template |

## 🚀 Next Steps Priority

1. **HIGH**: Run migrations (blocks everything)
2. **HIGH**: Configure Supermemory API key (blocks AI responses)
3. **MEDIUM**: Test chat functionality
4. **LOW**: Integrate course memory sync
5. **LOW**: Index existing courses

## 📖 Documentation

- **Full Guide**: See `CHAT_IMPLEMENTATION.md`
- **AI Assistant Guide**: See `.github/copilot-instructions.md`
- **Architecture**: See project's `AUTH_SYSTEM_SUMMARY.md` and `FRONTEND_DOCUMENTATION.md`
