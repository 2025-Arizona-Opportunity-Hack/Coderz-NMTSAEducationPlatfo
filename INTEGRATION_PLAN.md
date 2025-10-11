# Frontend-Backend Integration Plan

## Overview
This document outlines the complete integration strategy for connecting the React/TypeScript frontend with the Django backend.

## Current State Analysis

### Backend
- **Framework**: Django 5.2.7 with traditional SSR (Server-Side Rendering)
- **Port**: 8000 (typical Django development server)
- **Authentication**: 
  - OAuth (Auth0) for students/teachers - Session-based
  - Username/password for admins - Django authentication
- **Response Format**: Rendered HTML templates (not REST API)
- **Apps**: authentication, admin_dash, student_dash, teacher_dash, lms

### Frontend
- **Framework**: React + TypeScript + Vite
- **Port**: 5173 (Vite default)
- **API Base URL**: `http://localhost:3000/api` ❌ (Incorrect - needs to be 8000)
- **Authentication**: Expects JWT Bearer tokens
- **Expected Format**: JSON responses with `{data: T}` wrapper

### Key Mismatches Identified
1. **Port Mismatch**: Frontend points to 3000, Django runs on 8000
2. **API Prefix**: Frontend expects `/api/*`, backend has no such prefix
3. **Response Format**: Frontend expects JSON, backend returns HTML
4. **Authentication**: Frontend expects JWT, backend uses sessions
5. **Admin Authentication**: No separate admin login page/endpoint

---

## Integration Strategy

### Approach: Dual-Mode Backend
Instead of replacing the existing Django SSR application, we'll add a REST API layer alongside it:
- Keep existing Django views and templates for direct backend access
- Add new API endpoints under `/api/` prefix for frontend consumption
- Implement JWT authentication specifically for API endpoints
- Maintain session-based auth for SSR views

---

## Phase 1: Backend API Layer Setup

### 1.1 Install Required Packages
Add to `backend/nmtsa_lms/pyproject.toml`:
```toml
[tool.poetry.dependencies]
djangorestframework = "^3.14.0"
djangorestframework-simplejwt = "^5.3.1"
django-cors-headers = "^4.3.1"
```

### 1.2 Update Django Settings
In `backend/nmtsa_lms/nmtsa_lms/settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'api',  # New app for REST API
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add at top
    # ... existing middleware
]

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# JWT Configuration
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

### 1.3 Create API App
```bash
cd backend/nmtsa_lms
python manage.py startapp api
```

---

## Phase 2: API Endpoints Mapping

### 2.1 Authentication Endpoints

#### Backend: `api/views/auth.py`
```python
# /api/auth/admin/login
POST - Admin username/password login → Returns JWT tokens

# /api/auth/me
GET - Get current user profile

# /api/auth/logout
POST - Logout (optional for JWT, mainly clears client-side)
```

#### Frontend Service: `auth.service.ts`
- Update `signIn()` to support admin login with username/password
- Store JWT token in localStorage
- Add admin-specific login method

### 2.2 Course Endpoints

#### Backend: `api/views/courses.py`
```python
# /api/courses
GET - List courses (with filters: search, category, difficulty, price, etc.)
  Query params: page, limit, search, category, difficulty, sortBy, sortOrder
  Response: PaginatedResponse<Course>

# /api/courses/{id}
GET - Course details
  Response: Course

# /api/courses/{id}/detail
GET - Full course detail with modules, instructor, reviews
  Response: CourseDetail

# /api/courses/categories
GET - List of all categories
  Response: {data: string[]}

# /api/courses/featured
GET - Featured courses
  Query params: limit
  Response: {data: Course[]}

# /api/courses/{id}/enroll
POST - Enroll in course
  Response: Enrollment

DELETE - Unenroll from course

# /api/courses/{id}/reviews
GET - Course reviews with pagination
  Response: PaginatedResponse<Review>
```

### 2.3 Dashboard Endpoints

#### Backend: `api/views/dashboard.py`
```python
# /api/dashboard/stats
GET - User dashboard statistics
  Response: {data: DashboardStats}

# /api/dashboard/enrollments
GET - User enrollments with progress
  Query params: page, limit, status
  Response: PaginatedResponse<EnrollmentWithProgress>

# /api/dashboard/continue-learning
GET - Continue learning recommendations
  Response: {data: ContinueLearningItem[]}

# /api/dashboard/certificates
GET - User certificates
  Response: {data: Certificate[]}
```

### 2.4 Lesson Endpoints

#### Backend: `api/views/lessons.py`
```python
# /api/courses/{course_id}/lessons/{lesson_id}
GET - Lesson content with resources
  Response: {data: LessonContent}

# /api/courses/{course_id}/lessons/{lesson_id}/complete
POST - Mark lesson as complete
  Response: {data: LessonProgress}

# /api/courses/{course_id}/lessons/{lesson_id}/progress
PUT - Update lesson progress (time, position)
  Request: {timeSpent: number, lastPosition: number}
  Response: {data: LessonProgress}

# /api/courses/{course_id}/lessons/{lesson_id}/notes
GET - Get lesson notes (paginated)
  Response: PaginatedResponse<Note>

POST - Create note
  Request: {content: string, timestamp?: number}
  Response: {data: Note}

# /api/courses/{course_id}/lessons/{lesson_id}/notes/{note_id}
PUT - Update note
DELETE - Delete note
```

### 2.5 Forum Endpoints

#### Backend: `api/views/forum.py`
```python
# /api/forum/posts
GET - List all forum posts
  Query params: page, limit, search, sortBy, tags
  Response: PaginatedResponse<ForumPost>

POST - Create new post
  Request: {title: string, content: string, tags: string[]}
  Response: {data: ForumPost}

# /api/forum/posts/{post_id}
GET - Get post details with comments
  Response: {data: ForumPost}

PUT - Update post
DELETE - Delete post

# /api/forum/posts/{post_id}/comments
POST - Add comment
  Request: {content: string, parentId?: string}
  Response: {data: ForumComment}

# /api/forum/posts/{post_id}/like
POST - Toggle like on post
```

### 2.6 Applications Endpoints

#### Backend: `api/views/applications.py`
```python
# /api/applications
GET - Get user's applications
  Response: PaginatedResponse<Application>

POST - Submit new application
  Request: CreateApplicationDto
  Response: {data: Application}

# /api/applications/{app_id}
GET - Application details
  Response: {data: Application}

DELETE - Cancel application
```

---

## Phase 3: Model Serializers

### 3.1 Create Serializers
In `api/serializers.py`:

```python
from rest_framework import serializers
from authentication.models import User, TeacherProfile, StudentProfile, Enrollment
from teacher_dash.models import Course, Module, Lesson, VideoLesson, BlogLesson, DiscussionPost

class UserSerializer(serializers.ModelSerializer):
    """Maps to Profile type in frontend"""
    fullName = serializers.SerializerMethodField()
    avatarUrl = serializers.URLField(source='profile_picture', allow_null=True)
    
    def get_fullName(self, obj):
        return obj.get_full_name() or obj.username
    
    class Meta:
        model = User
        fields = ['id', 'email', 'fullName', 'role', 'avatarUrl', 'createdAt', 'updatedAt']

class CourseSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(source='published_by', read_only=True)
    difficulty = serializers.CharField(default='beginner')  # Add to model
    duration = serializers.IntegerField()  # Calculate from modules
    credits = serializers.IntegerField(default=0)  # Add to model
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'thumbnailUrl', 'instructor', 
                  'category', 'difficulty', 'duration', 'credits', 'rating', 
                  'enrollmentCount', 'createdAt', 'updatedAt']

# ... additional serializers for other models
```

---

## Phase 4: Database Model Updates

### 4.1 Course Model Enhancements
Add to `teacher_dash/models.py`:

```python
class Course(models.Model):
    # Existing fields...
    
    # New fields needed for frontend
    thumbnail_url = models.URLField(max_length=500, null=True, blank=True)
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced')
        ],
        default='beginner'
    )
    credits = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=100, default='General')
    long_description = models.TextField(null=True, blank=True)
    prerequisites = models.JSONField(default=list, blank=True)
    learning_objectives = models.JSONField(default=list, blank=True)
```

### 4.2 Enrollment Model Enhancements
Add to `authentication/models.py`:

```python
class Enrollment(models.Model):
    # Existing fields...
    
    # New fields
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    current_lesson = models.ForeignKey(
        'teacher_dash.Lesson',
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
```

### 4.3 Lesson Model Enhancements
Add to `teacher_dash/models.py`:

```python
class Lesson(models.Model):
    # Existing fields...
    
    # New fields
    description = models.TextField(default='')
    order = models.IntegerField(default=0)
    content_url = models.URLField(null=True, blank=True)
```

### 4.4 Create Migrations
```bash
cd backend/nmtsa_lms
python manage.py makemigrations
python manage.py migrate
```

---

## Phase 5: Frontend Updates

### 5.1 Update API Configuration
In `frontend/src/config/api.ts`:

```typescript
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";
```

### 5.2 Create AdminLogin Page
File: `frontend/src/pages/AdminLogin.tsx`

```tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "@/services/auth.service";

export default function AdminLogin() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await authService.adminSignIn({ username, password });
      navigate("/admin/dashboard");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    // ... form implementation
  );
}
```

### 5.3 Update Auth Service
In `frontend/src/services/auth.service.ts`:

```typescript
export interface AdminSignInData {
  username: string;
  password: string;
}

export const authService = {
  // ... existing methods
  
  async adminSignIn(data: AdminSignInData) {
    try {
      const response = await api.post<AuthResponse>("/auth/admin/login", data);
      const { token, user } = response.data;
      
      localStorage.setItem("auth-token", token);
      return { profile: user, token };
    } catch (error) {
      const apiError = error as ApiError;
      throw new Error(apiError.message || "Failed to sign in");
    }
  },
};
```

### 5.4 Update API Response Handling
Some endpoints may return direct data, others wrapped. Update service methods to handle both:

```typescript
// In each service file
const response = await api.get<Course>(`/courses/${id}`);
// Handle both formats: response.data or response.data.data
return response.data.data || response.data;
```

---

## Phase 6: URL Routing Updates

### 6.1 Add API URLs to Django
In `backend/nmtsa_lms/nmtsa_lms/urls.py`:

```python
urlpatterns = [
    # ... existing patterns
    path('api/', include('api.urls')),  # Add API routes
]
```

### 6.2 Create API URL Configuration
File: `backend/nmtsa_lms/api/urls.py`

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import auth, courses, dashboard, lessons, forum, applications

urlpatterns = [
    # Auth endpoints
    path('auth/admin/login', auth.AdminLoginView.as_view()),
    path('auth/me', auth.CurrentUserView.as_view()),
    
    # Course endpoints
    path('courses', courses.CourseListView.as_view()),
    path('courses/categories', courses.CategoryListView.as_view()),
    path('courses/featured', courses.FeaturedCoursesView.as_view()),
    path('courses/<int:pk>', courses.CourseDetailView.as_view()),
    path('courses/<int:pk>/detail', courses.CourseFullDetailView.as_view()),
    path('courses/<int:pk>/enroll', courses.EnrollmentView.as_view()),
    path('courses/<int:pk>/reviews', courses.CourseReviewsView.as_view()),
    
    # Dashboard endpoints
    path('dashboard/stats', dashboard.StatsView.as_view()),
    path('dashboard/enrollments', dashboard.EnrollmentsView.as_view()),
    path('dashboard/continue-learning', dashboard.ContinueLearningView.as_view()),
    path('dashboard/certificates', dashboard.CertificatesView.as_view()),
    
    # Lesson endpoints
    path('courses/<int:course_id>/lessons/<int:lesson_id>', lessons.LessonContentView.as_view()),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/complete', lessons.MarkCompleteView.as_view()),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/progress', lessons.ProgressUpdateView.as_view()),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/notes', lessons.NotesView.as_view()),
    
    # Forum endpoints
    path('forum/posts', forum.PostListView.as_view()),
    path('forum/posts/<int:pk>', forum.PostDetailView.as_view()),
    path('forum/posts/<int:pk>/comments', forum.CommentView.as_view()),
    path('forum/posts/<int:pk>/like', forum.LikeView.as_view()),
    
    # Applications endpoints
    path('applications', applications.ApplicationListView.as_view()),
    path('applications/<int:pk>', applications.ApplicationDetailView.as_view()),
]
```

---

## Phase 7: Testing Strategy

### 7.1 Backend API Testing
```bash
# Test with curl or httpie
http POST localhost:8000/api/auth/admin/login username=admin password=admin123

# Test authenticated endpoint
http GET localhost:8000/api/courses "Authorization: Bearer <token>"
```

### 7.2 Frontend Integration Testing
1. Start Django backend: `python manage.py runserver`
2. Start Vite frontend: `npm run dev`
3. Test admin login flow
4. Test course browsing
5. Test enrollment and dashboard

### 7.3 CORS Verification
Check browser console for CORS errors. If found:
- Verify CORS_ALLOWED_ORIGINS includes frontend URL
- Check credentials are allowed
- Verify middleware order

---

## Phase 8: Environment Configuration

### 8.1 Frontend Environment Variables
Create `frontend/.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### 8.2 Backend Environment Variables
Ensure `backend/nmtsa_lms/.env` has:

```env
DEBUG=True
SECRET_KEY=your-secret-key
AUTH0_DOMAIN=your-auth0-domain
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
```

---

## Known Issues and Solutions

### Issue 1: OAuth vs JWT for Students/Teachers
**Problem**: Frontend expects JWT, but students/teachers use OAuth with sessions.

**Solution**: 
- Create a bridge endpoint that converts OAuth session to JWT token
- After OAuth callback, generate JWT and pass to frontend
- Store JWT in localStorage alongside session

### Issue 2: Response Format Inconsistency
**Problem**: Some endpoints may return direct data, others wrapped in {data: T}.

**Solution**:
- Standardize all API responses to use {data: T} format
- Use DRF response wrapper
- Update frontend services to expect consistent format

### Issue 3: File Uploads
**Problem**: Course thumbnails, videos, resumes need proper handling.

**Solution**:
- Use Django's FileField for storage
- Serve media files through Django in development
- Return full URLs in API responses
- Configure MEDIA_URL and MEDIA_ROOT properly

### Issue 4: Pagination Format
**Problem**: Frontend expects specific pagination format.

**Solution**:
- Use DRF's PageNumberPagination
- Create custom pagination class if needed:
```python
class StandardPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    
    def get_paginated_response(self, data):
        return Response({
            'data': data,
            'pagination': {
                'page': self.page.number,
                'limit': self.page.paginator.per_page,
                'total': self.page.paginator.count,
                'totalPages': self.page.paginator.num_pages,
            }
        })
```

---

## Implementation Priority

1. **High Priority** (Core functionality):
   - API base URL update
   - Admin login page and endpoint
   - Course listing and detail endpoints
   - Authentication middleware

2. **Medium Priority** (User experience):
   - Dashboard statistics
   - Enrollment management
   - Lesson content delivery
   - Progress tracking

3. **Low Priority** (Enhancement features):
   - Forum/discussion endpoints
   - Certificate generation
   - Advanced filtering
   - Notes functionality

---

## Rollout Plan

### Week 1: Foundation
- Install packages
- Configure Django settings
- Create API app structure
- Set up CORS and JWT

### Week 2: Core APIs
- Implement auth endpoints
- Create course endpoints
- Build serializers
- Update database models

### Week 3: Frontend Integration
- Update API configuration
- Create AdminLogin page
- Update auth service
- Test basic flow

### Week 4: Additional Features
- Dashboard endpoints
- Lesson endpoints
- Progress tracking
- Full integration testing

---

## Success Metrics

- [ ] Frontend can successfully call backend APIs
- [ ] Admin can log in with username/password
- [ ] Students/teachers can browse courses
- [ ] Enrollment process works end-to-end
- [ ] Dashboard shows correct statistics
- [ ] Lesson content loads properly
- [ ] Progress tracking functions correctly
- [ ] No CORS errors in browser console
- [ ] All API responses follow consistent format

---

## Additional Considerations

### Security
- Implement rate limiting on auth endpoints
- Add CSRF protection for state-changing operations
- Validate all input data with serializers
- Use HTTPS in production

### Performance
- Add caching for frequently accessed data
- Optimize database queries with select_related/prefetch_related
- Implement database indexes on foreign keys
- Consider CDN for static assets

### Scalability
- Prepare for migration to production environment
- Consider separate API server if needed
- Plan for database scaling
- Implement proper logging and monitoring

---

## Documentation Updates Needed

1. Update README with new architecture
2. Document all API endpoints (consider Swagger/OpenAPI)
3. Create developer setup guide
4. Add troubleshooting section
5. Document environment variables

---

## Conclusion

This integration plan provides a comprehensive roadmap for connecting the frontend and backend. The dual-mode approach preserves existing functionality while adding modern REST API capabilities. By following this plan systematically, we can achieve a fully integrated full-stack application.
