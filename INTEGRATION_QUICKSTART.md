# NMTSA LMS - Frontend-Backend Integration Quick Start

## 📚 Documentation Overview

This project now has comprehensive documentation for frontend-backend integration:

1. **`BACKEND_API_DOCUMENTATION.md`** - Complete API reference with all endpoints, request/response formats
2. **`FRONTEND_BACKEND_INTEGRATION_SUMMARY.md`** - Detailed integration status, what's done, what's pending
3. **`BACKEND_APIS_TO_CREATE.md`** - Complete guide for creating missing REST APIs
4. **This file** - Quick start guide for developers

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (for Django backend)
- Node.js 18+ (for React frontend)
- pnpm (for frontend package management)

### 1. Start Backend (Django)

```bash
cd backend/nmtsa_lms

# Install dependencies (first time only)
pip install -r requirements.txt

# Run migrations (first time only)
python manage.py migrate

# Create admin user (optional, first time only)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Backend runs at: **http://localhost:8000**

### 2. Start Frontend (React + Vite)

```bash
cd frontend

# Install dependencies (first time only)
pnpm install

# Create .env file
cp .env.example .env  # Edit with your OAuth credentials

# Start development server
pnpm run dev
```

Frontend runs at: **http://localhost:5173**

---

## ✅ What's Working Now

### Fully Integrated APIs (Ready to Use):

1. **Authentication** ✅
   - Admin login (username/password)
   - OAuth sign-in (Google/Microsoft)
   - Get current user
   - Logout
   - Token refresh

2. **Profile & Onboarding** ✅
   - Get/update profile
   - Select role (student/teacher)
   - Teacher onboarding with file uploads
   - Student onboarding with profile data

3. **Courses** ✅
   - List courses with filters, search, pagination
   - Get course details
   - Get course categories
   - Get featured courses
   - Enroll/unenroll from courses
   - Get course reviews (placeholder)

4. **Dashboard** ✅
   - Dashboard statistics
   - Enrollments with progress
   - Continue learning recommendations
   - Certificates list

5. **Forum** ✅
   - List forum posts with filters
   - Create/update/delete posts
   - Get/create comments
   - Like/unlike posts and comments
   - Get forum tags

6. **Video Progress** ✅
   - Save video playback progress
   - Resume from last position

---

## ⚠️ What Needs Backend Work

### APIs That Need to Be Created:

These features exist in Django template views but need REST API endpoints:

1. **Lesson Content** ❌
   - View lesson (video/blog content)
   - Mark lesson complete
   - Update lesson progress

2. **Certificates** ❌
   - View certificate
   - Download certificate PDF

3. **Teacher Features** ❌
   - Course CRUD operations
   - Module CRUD operations
   - Lesson CRUD operations
   - Course analytics
   - Verification status

4. **Admin Features** ❌
   - Teacher verification (approve/reject)
   - Course review (approve/reject)
   - Admin dashboard stats

5. **Payment/Checkout** ❌
   - Initiate checkout
   - Process payment

6. **Course Discussions** ❌
   - Course-specific discussions (separate from forum)

**See `BACKEND_APIS_TO_CREATE.md` for detailed implementation guide**

---

## 🗂️ Project Structure

```
nmstaeducationlms/
├── backend/
│   └── nmtsa_lms/
│       ├── manage.py
│       ├── api/                    # REST API endpoints
│       │   ├── views/
│       │   │   ├── auth.py        ✅ Complete
│       │   │   ├── courses.py     ✅ Complete
│       │   │   ├── dashboard.py   ✅ Complete
│       │   │   ├── forum.py       ✅ Complete
│       │   │   └── profile.py     ✅ Complete
│       │   └── serializers.py     ✅ Updated
│       ├── authentication/         # User models, OAuth
│       ├── student_dash/          # Student template views
│       ├── teacher_dash/          # Teacher template views
│       └── admin_dash/            # Admin template views
│
└── frontend/
    └── src/
        ├── services/              # API integration
        │   ├── auth.service.ts   ✅ Complete
        │   ├── course.service.ts ✅ Complete
        │   ├── dashboard.service.ts ✅ Complete
        │   ├── forum.service.ts  ✅ Complete
        │   └── lesson.service.ts ⚠️ Placeholders only
        ├── types/
        │   └── api.ts            ✅ Updated to match backend
        ├── config/
        │   └── api.ts            ✅ Configured
        └── pages/                # React pages
```

---

## 🔑 Key Changes Made

### Frontend Changes:

1. **Type Definitions** (`frontend/src/types/api.ts`)
   - Changed "instructor" → "teacher" throughout
   - Added `UserProfile`, `TeacherProfile`, `StudentProfile`
   - Updated `Course` with `price`, `is_paid` fields
   - Updated lesson types to only "video" and "blog"

2. **Services Updated**:
   - `auth.service.ts` - Verified, working
   - `course.service.ts` - Updated query parameters
   - `dashboard.service.ts` - Verified, working
   - `forum.service.ts` - Major updates for backend format
   - `lesson.service.ts` - Placeholders + video progress endpoint

3. **API Config** (`frontend/src/config/api.ts`)
   - Points to `http://localhost:8000/api`
   - JWT token interceptor configured
   - Error handling with auto-logout on 401

### Backend Changes:
- ✅ **No changes made** (as requested)
- ❌ New REST APIs need to be created (see `BACKEND_APIS_TO_CREATE.md`)

---

## 🧪 Testing the Integration

### Test Authentication:
```bash
# From frontend console
import { authService } from './services/auth.service';

// Admin login
await authService.adminSignIn({
  username: 'admin',
  password: 'your_password'
});

// Get current user
const user = await authService.getCurrentUser();
console.log(user);
```

### Test Course Browsing:
```bash
# From frontend console
import { courseService } from './services/course.service';

// Get courses
const courses = await courseService.getCourses({
  page: 1,
  limit: 10,
  search: 'music',
  difficulty: 'beginner'
});
console.log(courses);

// Get course details
const course = await courseService.getCourseDetail('1');
console.log(course);
```

### Test Dashboard:
```bash
# From frontend console
import { dashboardService } from './services/dashboard.service';

// Get stats
const stats = await dashboardService.getStats();
console.log(stats);

// Get enrollments
const enrollments = await dashboardService.getEnrollments(1, 10);
console.log(enrollments);
```

### Test Forum:
```bash
# From frontend console
import { forumService } from './services/forum.service';

// Get posts
const posts = await forumService.getPosts(1, 12, '', [], 'recent');
console.log(posts);

// Create post
const newPost = await forumService.createPost({
  title: 'Test Post',
  content: 'This is a test',
  tags: ['test']
});
console.log(newPost);
```

---

## 🐛 Common Issues & Solutions

### Issue: CORS errors
**Solution**: Django CORS middleware is configured. Make sure backend is running on port 8000.

### Issue: 401 Unauthorized
**Solution**: 
1. Check if you're logged in: `localStorage.getItem('auth-token')`
2. Token might be expired - login again
3. Check if endpoint requires authentication

### Issue: Backend returns HTML instead of JSON
**Solution**: You're hitting a template-based view, not an API endpoint. Check the URL starts with `/api/`.

### Issue: Type errors in frontend
**Solution**: Frontend types have been updated to match backend. Run `pnpm install` and restart dev server.

---

## 📚 API Documentation

### Base URL
- Development: `http://localhost:8000/api`
- All authenticated endpoints require: `Authorization: Bearer <token>`

### Example API Call
```typescript
// Using the configured axios instance
import api from '@/config/api';

// GET request
const response = await api.get('/courses');

// POST request
const response = await api.post('/courses/1/enroll');

// POST with data
const response = await api.post('/forum/posts', {
  title: 'My Post',
  content: 'Post content',
  tags: ['tag1', 'tag2']
});
```

---

## 🔐 Environment Variables

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000/api
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_MICROSOFT_CLIENT_ID=your_microsoft_client_id
```

### Backend (settings.py or .env)
```bash
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

---

## 📊 Integration Status

| Feature | Backend API | Frontend Service | Status |
|---------|-------------|------------------|--------|
| Authentication | ✅ | ✅ | 🟢 Complete |
| Profile & Onboarding | ✅ | ✅ | 🟢 Complete |
| Course Browsing | ✅ | ✅ | 🟢 Complete |
| Course Enrollment | ✅ | ✅ | 🟢 Complete |
| Dashboard | ✅ | ✅ | 🟢 Complete |
| Forum | ✅ | ✅ | 🟢 Complete |
| Video Progress | ✅ | ✅ | 🟢 Complete |
| Lesson Content | ❌ | ⚠️ | 🔴 Backend Needed |
| Lesson Complete | ❌ | ⚠️ | 🔴 Backend Needed |
| Certificates | ❌ | ⚠️ | 🔴 Backend Needed |
| Teacher Management | ❌ | ⚠️ | 🔴 Backend Needed |
| Admin Management | ❌ | ⚠️ | 🔴 Backend Needed |
| Payment/Checkout | ❌ | ⚠️ | 🔴 Backend Needed |
| Course Discussions | ❌ | ⚠️ | 🔴 Backend Needed |

**Overall: ~55% Complete**

---

## 🎯 Next Steps for Full Integration

1. **Read `BACKEND_APIS_TO_CREATE.md`** for detailed implementation guide
2. **Create lesson content APIs** (high priority)
3. **Create teacher management APIs** (medium priority)
4. **Create admin management APIs** (medium priority)
5. **Create payment/checkout APIs** (lower priority)
6. **Test all new endpoints** with frontend services

---

## 📞 Need Help?

- **API Reference**: `BACKEND_API_DOCUMENTATION.md`
- **Integration Details**: `FRONTEND_BACKEND_INTEGRATION_SUMMARY.md`
- **Backend API Guide**: `BACKEND_APIS_TO_CREATE.md`
- **Backend Code**: Check `backend/nmtsa_lms/api/views/*.py`
- **Frontend Code**: Check `frontend/src/services/*.ts`

---

*Last Updated: 2025-10-11*
*Created by: GitHub Copilot*
