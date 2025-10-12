# NMTSA LMS - Backend API Documentation

## Overview
This document provides comprehensive documentation of all backend APIs, their endpoints, request/response formats, and functionality.

## Base URL
- **Development**: `http://localhost:8000/api`
- **Production**: TBD

## Authentication
All authenticated endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## 1. AUTHENTICATION ENDPOINTS

### 1.1 Admin Login
**Endpoint**: `POST /api/auth/admin/login`  
**Auth Required**: No  
**Description**: Admin username/password authentication

**Request Body**:
```json
{
  "username": "admin",
  "password": "password123"
}
```

**Success Response** (200):
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhb...",
  "refreshToken": "eyJ0eXAiOiJKV1QiLCJhb...",
  "user": {
    "id": "1",
    "email": "admin@example.com",
    "fullName": "Admin User",
    "role": "admin",
    "avatarUrl": null,
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z"
  }
}
```

**Error Responses**:
- `400`: Missing username/password
- `401`: Invalid credentials
- `403`: Not an admin user

---

### 1.2 OAuth Sign In
**Endpoint**: `POST /api/auth/oauth/signin`  
**Auth Required**: No  
**Description**: OAuth sign-in (frontend handles OAuth, backend creates/updates user)

**Request Body**:
```json
{
  "provider": "google",  // or "microsoft"
  "email": "user@example.com",
  "name": "John Doe",
  "picture": "https://..." // optional
}
```

**Success Response** (200):
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhb...",
  "refreshToken": "eyJ0eXAiOiJKV1QiLCJhb...",
  "user": {
    "id": "1",
    "email": "user@example.com",
    "fullName": "John Doe",
    "role": "student",
    "avatarUrl": "https://...",
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z"
  },
  "isNewUser": true  // indicates if onboarding is needed
}
```

---

### 1.3 Get Current User
**Endpoint**: `GET /api/auth/me`  
**Auth Required**: Yes  
**Description**: Get current authenticated user profile

**Success Response** (200):
```json
{
  "id": "1",
  "email": "user@example.com",
  "fullName": "John Doe",
  "role": "student",
  "avatarUrl": "https://...",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

---

### 1.4 Logout
**Endpoint**: `POST /api/auth/logout`  
**Auth Required**: Yes  
**Description**: Logout current user

**Success Response** (200):
```json
{
  "message": "Successfully logged out"
}
```

---

### 1.5 Refresh Token
**Endpoint**: `POST /api/auth/token/refresh`  
**Auth Required**: No (uses refresh token)  
**Description**: Get new access token using refresh token

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhb..."
}
```

**Success Response** (200):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhb..."
}
```

---

## 2. PROFILE & ONBOARDING ENDPOINTS

### 2.1 Get Profile
**Endpoint**: `GET /api/profile`  
**Auth Required**: Yes  
**Description**: Get complete user profile with role-specific data

**Success Response** (200):
```json
{
  "id": "1",
  "username": "user123",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student",
  "profile_picture": "https://...",
  "onboarding_complete": true,
  "is_active": true,
  "date_joined": "2024-01-01T00:00:00Z",
  "teacher_profile": null,
  "student_profile": {
    "relationship": "parent",
    "care_recipient_name": "Jane Doe",
    "care_recipient_age": 5,
    "special_needs": "...",
    "learning_goals": "...",
    "interests": "...",
    "accessibility_needs": "..."
  }
}
```

---

### 2.2 Update Profile
**Endpoint**: `PUT /api/profile`  
**Auth Required**: Yes  
**Description**: Update basic user information

**Request Body**:
```json
{
  "first_name": "John",
  "last_name": "Doe"
}
```

**Success Response** (200):
```json
{
  "message": "Profile updated successfully",
  "user": { /* full user profile */ }
}
```

---

### 2.3 Select Role
**Endpoint**: `POST /api/onboarding/select-role`  
**Auth Required**: Yes  
**Description**: Select user role during onboarding

**Request Body**:
```json
{
  "role": "student"  // or "teacher"
}
```

**Success Response** (200):
```json
{
  "message": "Role selected successfully",
  "role": "student"
}
```

---

### 2.4 Teacher Onboarding
**Endpoint**: `POST /api/onboarding/teacher`  
**Auth Required**: Yes  
**Content-Type**: `multipart/form-data`  
**Description**: Complete teacher onboarding

**Request Body (FormData)**:
- `bio` (string, optional)
- `credentials` (string, optional)
- `specialization` (string, optional)
- `years_experience` (integer, optional)
- `resume` (file, optional)
- `certifications` (file, optional)

**Success Response** (200):
```json
{
  "message": "Teacher onboarding completed successfully",
  "user": { /* full user profile with teacher_profile */ }
}
```

---

### 2.5 Student Onboarding
**Endpoint**: `POST /api/onboarding/student`  
**Auth Required**: Yes  
**Description**: Complete student onboarding

**Request Body**:
```json
{
  "relationship": "parent",
  "care_recipient_name": "Jane Doe",
  "care_recipient_age": 5,
  "special_needs": "...",
  "learning_goals": "...",
  "interests": "...",
  "accessibility_needs": "..."
}
```

**Success Response** (200):
```json
{
  "message": "Student onboarding completed successfully",
  "user": { /* full user profile with student_profile */ }
}
```

---

## 3. COURSE ENDPOINTS

### 3.1 List Courses
**Endpoint**: `GET /api/courses`  
**Auth Required**: No  
**Description**: Get paginated list of published courses with filtering

**Query Parameters**:
- `page` (integer, default: 1)
- `limit` (integer, default: 10, max: 100)
- `search` (string, optional) - search in title and description
- `category` (string, optional) - filter by category tag
- `difficulty` (string, optional) - beginner|intermediate|advanced
- `minPrice` (float, optional)
- `maxPrice` (float, optional)
- `minCredits` (integer, optional)
- `maxCredits` (integer, optional)
- `minRating` (float, optional)
- `sortBy` (string, default: newest) - popularity|newest|rating|title
- `sortOrder` (string, default: desc) - asc|desc

**Success Response** (200):
```json
{
  "data": [
    {
      "id": "1",
      "title": "Introduction to Music Therapy",
      "description": "Learn the basics...",
      "thumbnailUrl": "https://...",
      "instructor": {
        "id": "2",
        "fullName": "Dr. Jane Smith",
        "avatarUrl": "https://...",
        "bio": "Expert in music therapy",
        "credentials": "PhD in Music Therapy"
      },
      "instructorId": "2",
      "category": "Music Therapy",
      "difficulty": "beginner",
      "duration": 180,  // minutes
      "credits": 3,
      "rating": 4.5,
      "enrollmentCount": 150,
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z",
      "price": "99.99",
      "is_paid": true
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 50,
    "totalPages": 5
  }
}
```

---

### 3.2 Get Course Categories
**Endpoint**: `GET /api/courses/categories`  
**Auth Required**: No  
**Description**: Get list of all course categories

**Success Response** (200):
```json
{
  "data": [
    "Music Therapy",
    "Neurologic Music Therapy",
    "Special Education",
    "Healthcare"
  ]
}
```

---

### 3.3 Get Featured Courses
**Endpoint**: `GET /api/courses/featured`  
**Auth Required**: No  
**Description**: Get featured courses (top enrolled)

**Query Parameters**:
- `limit` (integer, default: 6)

**Success Response** (200):
```json
{
  "data": [
    /* array of course objects */
  ]
}
```

---

### 3.4 Get Course Detail
**Endpoint**: `GET /api/courses/{id}`  
**Auth Required**: No  
**Description**: Get basic course details

**Success Response** (200):
```json
{
  /* single course object */
}
```

---

### 3.5 Get Course Full Detail
**Endpoint**: `GET /api/courses/{id}/detail`  
**Auth Required**: No (but shows different data if authenticated)  
**Description**: Get full course details with modules and lessons

**Success Response** (200):
```json
{
  "id": "1",
  "title": "Introduction to Music Therapy",
  "description": "Learn the basics...",
  "longDescription": "This comprehensive course...",
  "thumbnailUrl": "https://...",
  "instructor": {
    "id": "2",
    "fullName": "Dr. Jane Smith",
    "avatarUrl": "https://...",
    "bio": "Expert in music therapy",
    "credentials": "PhD in Music Therapy"
  },
  "instructorId": "2",
  "category": "Music Therapy",
  "difficulty": "beginner",
  "duration": 180,
  "credits": 3,
  "rating": 4.5,
  "enrollmentCount": 150,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z",
  "price": "99.99",
  "is_paid": true,
  "prerequisites": ["Basic music knowledge"],
  "learningObjectives": ["Understand music therapy principles", "..."],
  "modules": [
    {
      "id": "1",
      "title": "Introduction",
      "description": "Getting started",
      "order": 0,
      "lessons": [
        {
          "id": "1",
          "title": "Welcome Video",
          "lesson_type": "video",
          "type": "video",
          "duration": 15,
          "order": 0,
          "isCompleted": false,
          "isLocked": false,
          "contentUrl": "/media/videos/...",
          "created_at": "2024-01-01T00:00:00Z"
        }
      ],
      "isCompleted": false
    }
  ],
  "isEnrolled": false,
  "progress": 0,
  "averageRating": 4.5,
  "totalReviews": 0
}
```

---

### 3.6 Enroll in Course
**Endpoint**: `POST /api/courses/{id}/enroll`  
**Auth Required**: Yes  
**Description**: Enroll authenticated user in course

**Success Response** (201):
```json
{
  "id": "1",
  "userId": "1",
  "courseId": "1",
  "progress": 0,
  "completedLessons": [],
  "enrolledAt": "2024-01-01T00:00:00Z",
  "completedAt": null
}
```

**Error Responses**:
- `400`: Already enrolled

---

### 3.7 Unenroll from Course
**Endpoint**: `DELETE /api/courses/{id}/enroll`  
**Auth Required**: Yes  
**Description**: Unenroll from course

**Success Response** (200):
```json
{
  "message": "Successfully unenrolled from course"
}
```

**Error Responses**:
- `404`: Not enrolled in this course

---

### 3.8 Get Course Reviews
**Endpoint**: `GET /api/courses/{id}/reviews`  
**Auth Required**: No  
**Description**: Get course reviews (placeholder - to be implemented)

**Query Parameters**:
- `page` (integer, default: 1)
- `limit` (integer, default: 10)

**Success Response** (200):
```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 0,
    "totalPages": 0
  }
}
```

---

## 4. DASHBOARD ENDPOINTS

### 4.1 Get Dashboard Stats
**Endpoint**: `GET /api/dashboard/stats`  
**Auth Required**: Yes  
**Description**: Get dashboard statistics for current user

**Success Response** (200):
```json
{
  "data": {
    "totalCourses": 5,
    "inProgressCourses": 3,
    "completedCourses": 2,
    "totalCertificates": 2,
    "totalLearningHours": 45,
    "currentStreak": 0,
    "longestStreak": 0
  }
}
```

---

### 4.2 Get Dashboard Enrollments
**Endpoint**: `GET /api/dashboard/enrollments`  
**Auth Required**: Yes  
**Description**: Get user enrollments with progress

**Query Parameters**:
- `page` (integer, default: 1)
- `limit` (integer, default: 10)
- `status` (string, optional) - in-progress|completed

**Success Response** (200):
```json
{
  "data": [
    {
      "id": "1",
      "userId": "1",
      "courseId": "1",
      "progress": 65,
      "completedLessons": ["1", "2", "3"],
      "enrolledAt": "2024-01-01T00:00:00Z",
      "completedAt": null,
      "lastAccessedAt": "2024-01-15T10:30:00Z",
      "currentLesson": {
        "id": "4",
        "title": "Advanced Techniques",
        "moduleTitle": "Module 2"
      },
      "course": {
        /* full course object */
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 5,
    "totalPages": 1
  }
}
```

---

### 4.3 Continue Learning
**Endpoint**: `GET /api/dashboard/continue-learning`  
**Auth Required**: Yes  
**Description**: Get continue learning recommendations

**Success Response** (200):
```json
{
  "data": [
    {
      "enrollment": {
        /* enrollment with progress */
      },
      "nextLesson": {
        "id": "4",
        "title": "Advanced Techniques",
        "type": "video",
        "duration": 20
      }
    }
  ]
}
```

---

### 4.4 Get Certificates
**Endpoint**: `GET /api/dashboard/certificates`  
**Auth Required**: Yes  
**Description**: Get user certificates

**Success Response** (200):
```json
{
  "data": [
    {
      "id": "1",
      "courseId": "1",
      "userId": "1",
      "course": {
        "id": "1",
        "title": "Introduction to Music Therapy",
        "instructor": "Dr. Jane Smith"
      },
      "completedAt": "2024-01-01T00:00:00Z",
      "certificateUrl": "/student/courses/1/certificate/"
    }
  ]
}
```

---

## 5. FORUM ENDPOINTS

### 5.1 List Forum Posts
**Endpoint**: `GET /api/forum/posts`  
**Auth Required**: Yes  
**Description**: Get paginated list of forum posts

**Query Parameters**:
- `page` (integer, default: 1)
- `limit` (integer, default: 12)
- `search` (string, optional) - search in title and content
- `tags[]` (array of strings, optional) - filter by tags
- `sortBy` (string, default: recent) - recent|popular

**Success Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "1",
      "title": "How to start with music therapy?",
      "content": "I'm new to music therapy and...",
      "excerpt": "I'm new to music therapy and...",
      "authorId": "1",
      "author": {
        "id": "1",
        "fullName": "John Doe",
        "avatarUrl": "https://...",
        "role": "student"
      },
      "tags": ["beginner", "music-therapy"],
      "likes": 5,
      "commentsCount": 3,
      "isLiked": false,
      "isPinned": false,
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 12,
    "total": 50,
    "totalPages": 5
  }
}
```

---

### 5.2 Create Forum Post
**Endpoint**: `POST /api/forum/posts`  
**Auth Required**: Yes  
**Description**: Create a new forum post

**Request Body**:
```json
{
  "title": "How to start with music therapy?",
  "content": "I'm new to music therapy and...",
  "tags": ["beginner", "music-therapy"]
}
```

**Success Response** (201):
```json
{
  "success": true,
  "message": "Forum post created successfully",
  "data": {
    /* forum post object */
  }
}
```

---

### 5.3 Get Forum Tags
**Endpoint**: `GET /api/forum/tags`  
**Auth Required**: Yes  
**Description**: Get all unique tags used in forum posts

**Success Response** (200):
```json
{
  "success": true,
  "data": ["beginner", "music-therapy", "advanced", "techniques"]
}
```

---

### 5.4 Get Forum Post Detail
**Endpoint**: `GET /api/forum/posts/{post_id}`  
**Auth Required**: Yes  
**Description**: Get a specific forum post

**Success Response** (200):
```json
{
  "success": true,
  "data": {
    /* forum post object */
  }
}
```

---

### 5.5 Update Forum Post
**Endpoint**: `PUT /api/forum/posts/{post_id}`  
**Auth Required**: Yes (author only)  
**Description**: Update a forum post

**Request Body**:
```json
{
  "title": "Updated title",
  "content": "Updated content",
  "tags": ["updated", "tags"]
}
```

**Success Response** (200):
```json
{
  "success": true,
  "message": "Post updated successfully",
  "data": {
    /* updated forum post object */
  }
}
```

---

### 5.6 Delete Forum Post
**Endpoint**: `DELETE /api/forum/posts/{post_id}`  
**Auth Required**: Yes (author or admin)  
**Description**: Delete a forum post

**Success Response** (204):
```json
{
  "success": true,
  "message": "Post deleted successfully"
}
```

---

### 5.7 Get Post Comments
**Endpoint**: `GET /api/forum/posts/{post_id}/comments`  
**Auth Required**: Yes  
**Description**: Get all comments for a forum post

**Success Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "1",
      "postId": "1",
      "content": "Great question! Here's my answer...",
      "authorId": "2",
      "author": {
        "id": "2",
        "fullName": "Jane Smith",
        "avatarUrl": "https://...",
        "role": "teacher"
      },
      "parentId": null,
      "replies": [
        {
          /* nested reply objects */
        }
      ],
      "likes": 2,
      "isLiked": false,
      "createdAt": "2024-01-01T01:00:00Z",
      "updatedAt": "2024-01-01T01:00:00Z"
    }
  ]
}
```

---

### 5.8 Create Comment
**Endpoint**: `POST /api/forum/posts/{post_id}/comments`  
**Auth Required**: Yes  
**Description**: Create a comment on a forum post

**Request Body**:
```json
{
  "content": "Great question! Here's my answer...",
  "parentId": null  // or comment ID if replying to a comment
}
```

**Success Response** (201):
```json
{
  "success": true,
  "message": "Comment created successfully",
  "data": {
    /* comment object */
  }
}
```

---

### 5.9 Like Post
**Endpoint**: `POST /api/forum/posts/{post_id}/like`  
**Auth Required**: Yes  
**Description**: Like a forum post

**Success Response** (201):
```json
{
  "success": true,
  "message": "Post liked successfully"
}
```

---

### 5.10 Unlike Post
**Endpoint**: `DELETE /api/forum/posts/{post_id}/like`  
**Auth Required**: Yes  
**Description**: Unlike a forum post

**Success Response** (204):
```json
{
  "success": true,
  "message": "Post unliked successfully"
}
```

---

### 5.11 Like Comment
**Endpoint**: `POST /api/forum/comments/{comment_id}/like`  
**Auth Required**: Yes  
**Description**: Like a forum comment

**Success Response** (201):
```json
{
  "success": true,
  "message": "Comment liked successfully"
}
```

---

### 5.12 Unlike Comment
**Endpoint**: `DELETE /api/forum/comments/{comment_id}/like`  
**Auth Required**: Yes  
**Description**: Unlike a forum comment

**Success Response** (204):
```json
{
  "success": true,
  "message": "Comment unliked successfully"
}
```

---

## 6. ADDITIONAL FUNCTIONALITY (Template-based, not yet API-exposed)

### Student Dashboard Functions (from templates):
- Dashboard overview
- Courses list (my courses)
- Catalog browsing
- Course checkout/payment
- Learning interface
- Lesson viewing (video/blog)
- Mark lesson complete
- Save video progress
- Certificates (view/download PDF)
- Course discussions (CRUD)

### Teacher Dashboard Functions (from templates):
- Dashboard overview
- Courses CRUD operations
- Modules CRUD operations
- Lessons CRUD operations
- Course preview
- Lesson preview
- Course analytics
- Verification status
- Course publish/unpublish
- Export courses
- Course discussions

### Admin Dashboard Functions (from templates):
- Dashboard overview
- Verify teachers (approve/reject)
- Review courses (approve/reject with feedback)
- Course preview

---

## Notes:
1. All authenticated endpoints require JWT token in Authorization header
2. All timestamps are in ISO 8601 format (UTC)
3. All IDs are strings
4. All paginated responses follow the same structure
5. File uploads use multipart/form-data
6. Most endpoints return camelCase field names for frontend compatibility

## TODO APIs (Functionality exists but not exposed as REST API):
1. Lesson content viewing API
2. Mark lesson complete API
3. Save video progress API
4. Teacher course management APIs
5. Teacher analytics APIs
6. Admin verification APIs
7. Admin course review APIs
