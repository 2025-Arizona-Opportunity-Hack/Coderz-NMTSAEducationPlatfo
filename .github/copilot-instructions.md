# NMTSA LMS - AI Coding Assistant Instructions

## Project Overview
Django-based LMS for neurologic music therapy education with **dual authentication** (OAuth for students/teachers, Django admin for admins), autism-friendly UI, and comprehensive course management. Built for NMTSA to serve healthcare professionals and families with special needs.

## Architecture & File Structure

### Multi-App Django Structure
```
nmtsa_lms/                          # Django project root
├── nmtsa_lms/                      # Core project module
│   ├── settings.py                 # Auth0 config, custom User model, apps
│   ├── urls.py                     # Root URL routing (includes app URLs)
│   ├── views.py                    # Auth0 OAuth flow (login/callback/logout)
│   ├── static/css/                 # Tailwind input/output (npm run dev/build)
│   └── templates/                  # Base templates + components
│       ├── base.html               # Theme system (4 themes, font controls)
│       ├── landing.html            # Public homepage
│       └── components/             # Reusable UI (navbar, sidebar, cards)
├── authentication/                 # Custom User + profiles
│   ├── models.py                   # User, TeacherProfile, StudentProfile, Enrollment
│   ├── decorators.py               # RBAC (@teacher_required, @student_required, @admin_required)
│   ├── middleware.py               # Auth0UserSyncMiddleware (syncs session ↔ DB)
│   ├── views.py                    # Onboarding (select_role, teacher/student onboarding)
│   └── admin_views.py              # Admin username/password login
├── teacher_dash/                   # Teacher features
│   ├── models.py                   # Course, Module, Lesson, VideoLesson, BlogLesson, DiscussionPost
│   ├── views.py                    # Course CRUD, lesson upload, review workflow
│   ├── forms.py                    # Course/lesson forms with validation
│   └── management/commands/        # seed_demo_courses, import_courses
├── student_dash/                   # Student features (enrollment, progress)
├── admin_dash/                     # Admin verification + course review
└── lms/                            # Shared LMS logic
    └── models.py                   # CompletedLesson, VideoProgress
```

### Key Conventions
- **Custom User Model**: `authentication.User` (extends `AbstractUser`) - set as `AUTH_USER_MODEL` in settings
- **Templates**: Centralized in `nmtsa_lms/templates/` + app-specific in `{app}/templates/{app}/`
- **Media Files**: Uploaded to `media/` (videos, resumes, certifications, blog images)
- **Static Assets**: Tailwind CSS compiled via `npm run dev/build` from `input.css` → `output.css`

## Authentication System (Critical)

### Dual Auth Architecture
1. **OAuth (Auth0)** → Students & Teachers
   - Flow: `/login` → Auth0 → `/callback` → role selection → onboarding → dashboard
   - Session key: `request.session['user']` (contains `userinfo`, `role`, `onboarding_complete`)
   - Middleware: `Auth0UserSyncMiddleware` syncs Auth0 data to local `User` model on every request
   
2. **Django Admin** → Admins only
   - Separate login at `/auth/admin-login/` using `django.contrib.auth.authenticate()`
   - Admins CANNOT use OAuth (blocked in role selection)
   - Uses `@admin_required` decorator (checks `request.user.is_authenticated` + `role='admin'`)

### OAuth Flow Details
```python
# nmtsa_lms/views.py
oauth = OAuth()  # Global instance - DO NOT recreate
oauth.register("auth0", ...)  # Configured with AUTH0_* env vars

# Login: oauth.auth0.authorize_redirect()
# Callback: Checks user.role + onboarding_complete → redirects:
#   - No role → select_role
#   - Role but not onboarded → teacher_onboarding / student_onboarding
#   - Onboarded → teacher_dashboard / student_dashboard
```

### RBAC Decorators (Use These!)
```python
from authentication.decorators import (
    login_required,              # OAuth session check
    student_required,            # Role = student
    teacher_required,            # Role = teacher
    admin_required,              # Django auth + role = admin
    teacher_verified_required,   # Teacher + verification_status = approved
    onboarding_complete_required # user.onboarding_complete = True
)

# Example usage
@teacher_required
@onboarding_complete_required
def create_course(request):
    teacher = _get_logged_in_teacher(request)  # Helper in teacher_dash/views.py
    # ... course creation logic
```

### Teacher Verification Workflow
1. Teacher completes onboarding → `TeacherProfile.verification_status = 'pending'`
2. Admin reviews at `/admin-dash/verify-teachers/` → approves/rejects
3. Only **approved** teachers can create/edit courses (checked via `_check_teacher_approval()`)

## Course & Lesson Management

### Data Model Hierarchy
```
Course (teacher_dash.Course)
├── is_published (bool)
├── is_submitted_for_review (bool)
├── admin_approved (bool)
├── is_paid (bool) + price
├── modules (M2M → Module)
└── discussions (FK ← DiscussionPost)

Module
└── lessons (M2M → Lesson)

Lesson (base)
├── lesson_type ('video' | 'blog')
├── duration (minutes)
└── OneToOne → VideoLesson OR BlogLesson

VideoLesson
├── video_file (FileField → media/videos/)
└── transcript (TextField)

BlogLesson
├── content (TextField)
└── images (ImageField → media/blog_images/)
```

### Course Review Workflow (Important!)
1. Teacher creates course → `is_published=False`, `is_submitted_for_review=False`
2. Teacher submits → `is_submitted_for_review=True` (cannot edit while in review)
3. Admin reviews at `/admin-dash/review-courses/` → approves/rejects with feedback
4. If approved → `admin_approved=True`, teacher can publish
5. **If teacher edits published course** → automatically unpublished + resubmitted for review (see `_handle_course_content_change()`)

### Video Handling
- Videos stored in `media/videos/` via `VideoLesson.video_file`
- Progress tracked in `lms.VideoProgress` (last_position_seconds, completed_percentage)
- Use `moviepy` (in dependencies) for video processing if needed

## Student Progress Tracking

### Enrollment & Completion
```python
# authentication/models.py
Enrollment (Student ↔ Course)
├── progress_percentage (auto-calculated)
├── completed (bool)
└── completed_lessons (FK ← lms.CompletedLesson)

# lms/models.py
CompletedLesson (Enrollment ↔ Lesson)  # Unique together
VideoProgress (Enrollment ↔ Lesson)     # Resume video playback
```

## Frontend (Autism-Friendly Design)

### Theme System (base.html)
- 4 themes: Light, Dark, High Contrast, Minimal
- Font size controls: Small, Medium, Large
- JavaScript persistence via `localStorage.getItem/setItem('nmtsa-theme')`
- **Zero animations/auto-play** (WCAG 2.1 AAA)

### Component Usage
```django
{# Include reusable components #}
{% include 'components/navbar.html' %}
{% include 'components/sidebar.html' %}
{% include 'components/card.html' with title="Course Title" %}
{% include 'components/button.html' with text="Enroll" style="primary" %}
```

### Tailwind Workflow
```bash
cd nmtsa_lms
npm install                  # Install tailwindcss
npm run dev                  # Watch mode (development)
npm run build                # Minified (production)
```

## Development Workflow

### Environment Setup
```bash
# 1. Activate virtual env (uv manages automatically or manual):
.venv/Scripts/activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 2. Set up .env file (root directory):
AUTH0_DOMAIN=your-tenant.us.auth0.com
AUTH0_CLIENT_ID=...
AUTH0_CLIENT_SECRET=...

# 3. Apply migrations:
cd nmtsa_lms
python manage.py migrate

# 4. Create admin superuser:
python manage.py createsuperuser
# Then in Django admin: set role='admin', onboarding_complete=True

# 5. Run dev server:
python manage.py runserver
```

### Testing User Flows
```bash
# Seed demo data:
python manage.py seed_demo_courses  # Creates sample courses

# Test as different roles:
# 1. Student: Sign up via OAuth → select "Student/Family" → onboard → dashboard
# 2. Teacher: Sign up via OAuth → select "Educator/Therapist" → upload credentials → pending verification
# 3. Admin: Log in at /auth/admin-login/ → verify teacher → review courses
```

### Common Gotchas
1. **Session vs User model**: OAuth decorators check `request.session['user']`, admin decorator checks `request.user.is_authenticated`
2. **Template paths**: Use app prefixes (`{% extends "base.html" %}` works, app templates need `app/template.html`)
3. **Media files**: Must add `+ static(settings.MEDIA_URL, ...)` to `urlpatterns` in DEBUG mode (already done)
4. **Course editing**: Published courses auto-unpublish on edit (see `_handle_course_content_change()`)
5. **Teacher verification**: Check `_check_teacher_approval()` before allowing course operations

## Key Files to Reference

- **Auth flow**: `nmtsa_lms/views.py` (OAuth), `authentication/views.py` (onboarding)
- **RBAC logic**: `authentication/decorators.py`, `authentication/middleware.py`
- **Course operations**: `teacher_dash/views.py` (1000+ lines, well-documented helpers)
- **Models**: `authentication/models.py`, `teacher_dash/models.py`, `lms/models.py`
- **UI components**: `nmtsa_lms/templates/components/` (navbar, sidebar, cards, etc.)

## Chat System with Supermemory AI

### Architecture
- **Frontend**: Single-file modular JavaScript (`static/js/chat.js`)
- **Backend**: REST APIs in `lms/views.py`
- **AI Engine**: Supermemory for memory-enhanced responses
- **Availability**: All users (authenticated or not)

### Key Files
- **Chat Component**: `templates/components/chat.html`
- **Chat Manager**: `static/js/chat.js` (ChatManager class)
- **Backend APIs**: `lms/views.py` (chat_*, search_courses_semantic)
- **Supermemory Client**: `lms/supermemory_client.py`
- **Course Memory**: `lms/course_memory.py` (sync courses to memory)

### API Endpoints
```
GET  /lms/api/chat/rooms/                    # List chat rooms
GET  /lms/api/chat/rooms/<id>/messages/      # Get message history
POST /lms/api/chat/rooms/<id>/send/          # Send message (triggers AI response)
POST /lms/api/chat/rooms/<id>/typing/        # Update typing indicator
GET  /lms/api/chat/rooms/<id>/typing/status/ # Get who's typing
POST /lms/api/courses/search/                # Semantic course search
```

### Supermemory Integration
```python
from lms.supermemory_client import get_supermemory_client

supermemory = get_supermemory_client()

# AI chat completion with memory
response = supermemory.chat_completion(
    messages=[{'role': 'user', 'content': 'Help me find courses'}],
    use_memory=True
)

# Add to memory (auto-context for future queries)
supermemory.add_memory(
    content="User enrolled in NMT Basics",
    metadata={'type': 'enrollment', 'user_id': user.id}
)

# Semantic search courses
courses = supermemory.search_courses(query="autism therapy", limit=10)
```

### Adding Courses to Memory
```python
from lms.course_memory import add_course_to_memory

# When creating/updating courses
add_course_to_memory({
    'id': course.id,
    'title': course.title,
    'description': course.description,
    'tags': list(course.tags.names()),
    'modules': [{'title': m.title} for m in course.modules.all()]
})
```

### Environment Setup
```bash
# Add to .env
SUPERMEMORY_API_KEY=your-api-key
SUPERMEMORY_BASE_URL=https://api.supermemory.ai
SUPERMEMORY_PROJECT_ID=nmtsa-lms
```

## Project Goals (Context)
Built for 24-hour hackathon targeting NMTSA's dual audience:
- **Healthcare professionals**: Continuing education, certification tracking
- **Families/caregivers**: Special needs resources, therapy education
- **Priority features**: Auth (10/10), Course management (10/10), Student progress (9/10), Video player (10/10), AI Chat (10/10)
