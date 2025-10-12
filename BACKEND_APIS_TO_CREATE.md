# Backend APIs That Need to Be Created

## Overview
This document lists all the backend REST API endpoints that need to be created to fully integrate the Django template-based views with the React frontend. The backend has extensive functionality in template views that isn't exposed as REST APIs yet.

---

## 🔴 HIGH PRIORITY - Core Learning Features

### 1. Lesson Content API
**Purpose**: View lesson content (video/blog) with resources and navigation

```python
# File: backend/nmtsa_lms/api/views/lessons.py (NEW)

GET /api/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}
- Returns: Full lesson content including video URL or blog HTML
- Include: Next/previous lesson navigation, resources, completed status
- Serializer needed: LessonContentSerializer

Response:
{
  "id": "1",
  "title": "Introduction to Music Therapy",
  "type": "video",
  "duration": 15,
  "contentUrl": "/media/videos/lesson1.mp4",
  "transcript": "...",
  "blogContent": null,  // or HTML for blog lessons
  "resources": [...],
  "nextLesson": {...},
  "previousLesson": {...},
  "isCompleted": false,
  "lastPosition": 0  // for video
}
```

**Current Backend**: Template view at `/student/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/`

**Recommendation**: Extract logic from `student_dash.views.lesson_view()` and create REST API version

---

### 2. Mark Lesson Complete API
**Purpose**: Mark a lesson as completed

```python
POST /api/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/complete
- Returns: Updated lesson progress
- Creates CompletedLesson entry
- Updates enrollment progress percentage

Response:
{
  "lessonId": "1",
  "courseId": "1",
  "isCompleted": true,
  "completedAt": "2024-01-15T10:30:00Z",
  "progress": {
    "completedLessons": 5,
    "totalLessons": 10,
    "percentage": 50
  }
}
```

**Current Backend**: Template POST to `/student/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/complete/`

**Recommendation**: Extract logic from `student_dash.views.mark_lesson_complete()` and create REST API version

---

### 3. Certificate APIs
**Purpose**: View and download course certificates

```python
# View certificate data
GET /api/certificates/{enrollment_id}
- Returns: Certificate information for display

Response:
{
  "id": "1",
  "enrollmentId": "1",
  "courseId": "1",
  "userId": "1",
  "course": {
    "title": "Introduction to Music Therapy",
    "instructor": "Dr. Jane Smith",
    "credits": 3
  },
  "completedAt": "2024-01-15T10:30:00Z",
  "certificateNumber": "NMTSA-2024-001",
  "downloadUrl": "/api/certificates/1/pdf"
}

# Download certificate PDF
GET /api/certificates/{enrollment_id}/pdf
- Returns: PDF file (application/pdf)
- Generate certificate with course and user details
```

**Current Backend**: 
- View: `/student/courses/<course_id>/certificate/`
- PDF: `/student/courses/<course_id>/certificate.pdf`

**Recommendation**: Extract logic from `student_dash.views.certificate()` and `certificate_pdf()` and create REST API versions

---

## 🟡 MEDIUM PRIORITY - Teacher Features

### 4. Teacher Dashboard API
**Purpose**: Get teacher dashboard statistics

```python
GET /api/teacher/dashboard
- Returns: Teacher-specific dashboard stats

Response:
{
  "totalCourses": 5,
  "publishedCourses": 3,
  "draftCourses": 2,
  "totalStudents": 150,
  "totalRevenue": "4500.00",
  "pendingVerification": false,
  "verificationStatus": "approved",
  "recentEnrollments": [...]
}
```

**Current Backend**: Template view at `/teacher/`

**Recommendation**: Create new API view in `api/views/teacher.py`

---

### 5. Teacher Course Management APIs
**Purpose**: CRUD operations for teacher's courses

```python
# List teacher's courses
GET /api/teacher/courses
- Returns: Paginated list of teacher's courses

# Create course
POST /api/teacher/courses
Request:
{
  "title": "New Course",
  "description": "...",
  "price": "99.99",
  "difficulty": "beginner",
  "category": "Music Therapy",
  ...
}

# Update course
PUT /api/teacher/courses/{id}
Request: (same as create)

# Delete course
DELETE /api/teacher/courses/{id}

# Publish/Unpublish
POST /api/teacher/courses/{id}/publish
POST /api/teacher/courses/{id}/unpublish
```

**Current Backend**: Multiple views in `teacher_dash.views`
- `course_create()`, `course_edit()`, `course_delete()`
- `course_publish()`, `course_unpublish()`

**Recommendation**: Create new API views in `api/views/teacher.py` with proper serializers

---

### 6. Module Management APIs
**Purpose**: CRUD operations for course modules

```python
# Create module
POST /api/teacher/courses/{course_id}/modules
Request:
{
  "title": "Module 1: Introduction",
  "description": "...",
  "order": 1
}

# Update module
PUT /api/teacher/courses/{course_id}/modules/{module_id}

# Delete module
DELETE /api/teacher/courses/{course_id}/modules/{module_id}
```

**Current Backend**: Views in `teacher_dash.views`
- `module_create()`, `module_edit()`, `module_delete()`

**Recommendation**: Add to `api/views/teacher.py`

---

### 7. Lesson Management APIs
**Purpose**: CRUD operations for lessons

```python
# Create lesson
POST /api/teacher/courses/{course_id}/modules/{module_id}/lessons
Request (multipart/form-data):
{
  "title": "Lesson 1",
  "lesson_type": "video",
  "duration": 15,
  "video_file": <file>,  // for video lessons
  "transcript": "...",
  // OR
  "content": "<html>...",  // for blog lessons
  "images": <file>
}

# Update lesson
PUT /api/teacher/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}

# Delete lesson
DELETE /api/teacher/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}
```

**Current Backend**: Views in `teacher_dash.views`
- `lesson_create()`, `lesson_edit()`, `lesson_delete()`

**Recommendation**: Add to `api/views/teacher.py` with file upload support

---

### 8. Course Analytics API
**Purpose**: Get course performance metrics

```python
GET /api/teacher/courses/{course_id}/analytics
- Returns: Course analytics data

Response:
{
  "courseId": "1",
  "totalEnrollments": 150,
  "activeEnrollments": 120,
  "completedEnrollments": 30,
  "averageProgress": 65,
  "averageRating": 4.5,
  "revenue": "14950.00",
  "enrollmentsByWeek": [...],
  "completionRate": 20,
  "studentEngagement": {
    "averageTimeSpent": 180,
    "lessonsCompleted": 450,
    "discussionPosts": 75
  }
}
```

**Current Backend**: View at `/teacher/courses/<course_id>/analytics/`
- `teacher_dash.views.course_analytics()`

**Recommendation**: Create comprehensive analytics serializer and API view

---

### 9. Teacher Verification Status API
**Purpose**: Get teacher verification status

```python
GET /api/teacher/verification
- Returns: Verification status and details

Response:
{
  "verificationStatus": "pending",  // pending|approved|rejected
  "submittedAt": "2024-01-01T00:00:00Z",
  "verifiedAt": null,
  "feedback": null,
  "canCreateCourses": false,
  "canPublishCourses": false,
  "documentsSubmitted": {
    "resume": true,
    "certifications": true
  }
}
```

**Current Backend**: View at `/teacher/verification/`
- `teacher_dash.views.verification_status()`

**Recommendation**: Add to `api/views/teacher.py`

---

## 🟡 MEDIUM PRIORITY - Admin Features

### 10. Admin Dashboard API
**Purpose**: Get admin dashboard statistics

```python
GET /api/admin/dashboard
- Returns: Admin-specific dashboard stats

Response:
{
  "totalUsers": 500,
  "totalStudents": 450,
  "totalTeachers": 45,
  "totalAdmins": 5,
  "pendingTeacherVerifications": 10,
  "pendingCourseReviews": 5,
  "totalCourses": 50,
  "publishedCourses": 40,
  "totalEnrollments": 1500,
  "recentActivity": [...]
}
```

**Current Backend**: View at `/admin-dash/`
- `admin_dash.views.dashboard()`

**Recommendation**: Create new `api/views/admin.py` with admin-specific views

---

### 11. Teacher Verification APIs
**Purpose**: Manage teacher verification requests

```python
# List pending teachers
GET /api/admin/teachers/pending
- Returns: Paginated list of pending teacher verifications

Response:
{
  "data": [
    {
      "teacherId": "1",
      "user": {
        "id": "1",
        "fullName": "Jane Smith",
        "email": "jane@example.com"
      },
      "profile": {
        "bio": "...",
        "credentials": "...",
        "specialization": "Music Therapy",
        "years_experience": 5,
        "resumeUrl": "/media/teacher_resumes/...",
        "certificationsUrl": "/media/teacher_certifications/..."
      },
      "submittedAt": "2024-01-01T00:00:00Z",
      "verificationStatus": "pending"
    }
  ],
  "pagination": {...}
}

# Verify/Reject teacher
POST /api/admin/teachers/{teacher_id}/verify
Request:
{
  "action": "approve",  // or "reject"
  "feedback": "Credentials verified and approved."
}

Response:
{
  "message": "Teacher verified successfully",
  "teacher": {...}
}
```

**Current Backend**: Views in `admin_dash.views`
- `verify_teachers()`, `verify_teacher_action()`

**Recommendation**: Create `api/views/admin.py` with proper serializers

---

### 12. Course Review APIs
**Purpose**: Manage course review/approval process

```python
# List courses pending review
GET /api/admin/courses/pending
- Returns: Paginated list of courses pending review

Response:
{
  "data": [
    {
      "courseId": "1",
      "title": "Introduction to Music Therapy",
      "teacher": {...},
      "submittedAt": "2024-01-01T00:00:00Z",
      "reviewStatus": "pending",
      "previewUrl": "/api/admin/courses/1/preview"
    }
  ],
  "pagination": {...}
}

# Review/Approve course
POST /api/admin/courses/{course_id}/review
Request:
{
  "action": "approve",  // or "reject"
  "feedback": "Course content meets all quality standards."
}

# Preview course for review
GET /api/admin/courses/{course_id}/preview
- Returns: Full course details with modules and lessons
```

**Current Backend**: Views in `admin_dash.views`
- `review_courses()`, `review_course_action()`, `admin_course_preview()`

**Recommendation**: Add to `api/views/admin.py`

---

## 🟢 LOWER PRIORITY - Payment & Checkout

### 13. Checkout API
**Purpose**: Initiate course purchase

```python
POST /api/courses/{course_id}/checkout
Request:
{
  "paymentMethod": "stripe",  // or other payment providers
  "couponCode": "DISCOUNT20"  // optional
}

Response:
{
  "checkoutId": "checkout_123",
  "courseId": "1",
  "course": {...},
  "pricing": {
    "originalPrice": "99.99",
    "discount": "19.99",
    "finalPrice": "80.00"
  },
  "paymentIntent": "...",  // Stripe payment intent or similar
  "clientSecret": "..."
}
```

**Current Backend**: View at `/student/courses/<course_id>/checkout/`
- `student_dash.views.checkout_course()`

**Recommendation**: Create `api/views/payment.py` with payment provider integration

---

### 14. Payment Processing API
**Purpose**: Process course payment

```python
POST /api/courses/{course_id}/payment
Request:
{
  "checkoutId": "checkout_123",
  "paymentMethodId": "pm_123",  // Stripe payment method
  "billingDetails": {...}
}

Response:
{
  "success": true,
  "enrollmentId": "1",
  "transactionId": "txn_123",
  "receipt": {
    "receiptUrl": "...",
    "receiptNumber": "...",
    "amount": "80.00",
    "date": "2024-01-15T10:30:00Z"
  }
}
```

**Current Backend**: View at `/student/courses/<course_id>/process-payment/`
- `student_dash.views.process_checkout()`

**Recommendation**: Add to `api/views/payment.py`

---

## 🟢 LOWER PRIORITY - Course Discussions

### 15. Course Discussion APIs
**Purpose**: Manage course-specific discussions (separate from general forum)

```python
# List course discussions
GET /api/courses/{course_id}/discussions
- Returns: Paginated list of discussions for specific course

# Create discussion
POST /api/courses/{course_id}/discussions
Request:
{
  "content": "I have a question about...",
  "parentPostId": null  // or ID for replies
}

# Update discussion
PUT /api/courses/{course_id}/discussions/{post_id}

# Delete discussion
DELETE /api/courses/{course_id}/discussions/{post_id}

# Pin/Unpin discussion (teacher only)
POST /api/courses/{course_id}/discussions/{post_id}/pin
```

**Current Backend**: Views in both `student_dash.views` and `teacher_dash.views`
- `course_discussions()`, `discussion_create()`, `discussion_detail()`
- `discussion_reply()`, `discussion_edit()`, `discussion_delete()`
- `discussion_pin_toggle()` (teacher only)

**Recommendation**: Create `api/views/discussions.py` with proper permissions

---

## 📋 SERIALIZERS NEEDED

To implement the above APIs, create these serializer files:

### 1. Lesson Serializers
**File**: `backend/nmtsa_lms/api/serializers/lessons.py` (NEW)

```python
class VideoLessonContentSerializer(serializers.ModelSerializer):
    """Video lesson with transcript and video URL"""
    
class BlogLessonContentSerializer(serializers.ModelSerializer):
    """Blog lesson with HTML content and images"""
    
class LessonContentSerializer(serializers.ModelSerializer):
    """Combined lesson serializer with navigation"""
    video = VideoLessonContentSerializer(read_only=True)
    blog = BlogLessonContentSerializer(read_only=True)
    next_lesson = LessonSerializer(read_only=True)
    previous_lesson = LessonSerializer(read_only=True)

class LessonProgressUpdateSerializer(serializers.Serializer):
    """Update lesson progress"""
    time_spent = serializers.IntegerField()
    last_position = serializers.IntegerField()
```

### 2. Teacher Management Serializers
**File**: `backend/nmtsa_lms/api/serializers/teacher.py` (NEW)

```python
class TeacherDashboardStatsSerializer(serializers.Serializer):
    """Teacher dashboard statistics"""
    
class TeacherCourseSerializer(serializers.ModelSerializer):
    """Teacher's course with edit capabilities"""
    
class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/Update course"""
    
class ModuleCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/Update module"""
    
class LessonCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/Update lesson with file uploads"""
    
class CourseAnalyticsSerializer(serializers.Serializer):
    """Course analytics data"""
```

### 3. Admin Management Serializers
**File**: `backend/nmtsa_lms/api/serializers/admin.py` (NEW)

```python
class AdminDashboardStatsSerializer(serializers.Serializer):
    """Admin dashboard statistics"""
    
class PendingTeacherSerializer(serializers.ModelSerializer):
    """Teacher pending verification with documents"""
    
class TeacherVerificationActionSerializer(serializers.Serializer):
    """Approve/Reject teacher verification"""
    
class PendingCourseSerializer(serializers.ModelSerializer):
    """Course pending review"""
    
class CourseReviewActionSerializer(serializers.Serializer):
    """Approve/Reject course"""
```

### 4. Payment Serializers
**File**: `backend/nmtsa_lms/api/serializers/payment.py` (NEW)

```python
class CheckoutSerializer(serializers.Serializer):
    """Checkout initiation"""
    
class PaymentSerializer(serializers.Serializer):
    """Payment processing"""
    
class ReceiptSerializer(serializers.Serializer):
    """Payment receipt"""
```

### 5. Certificate Serializers
**File**: `backend/nmtsa_lms/api/serializers/certificates.py` (NEW)

```python
class CertificateSerializer(serializers.ModelSerializer):
    """Certificate data for display"""
```

---

## 🎯 IMPLEMENTATION PRIORITY

### Phase 1 - Core Learning (Week 1-2)
1. ✅ Lesson Content API
2. ✅ Mark Lesson Complete API
3. ✅ Certificate APIs

### Phase 2 - Teacher Features (Week 3-4)
4. ✅ Teacher Dashboard API
5. ✅ Course Management APIs
6. ✅ Module Management APIs
7. ✅ Lesson Management APIs
8. ✅ Course Analytics API
9. ✅ Teacher Verification Status API

### Phase 3 - Admin Features (Week 5)
10. ✅ Admin Dashboard API
11. ✅ Teacher Verification APIs
12. ✅ Course Review APIs

### Phase 4 - Payment (Week 6)
13. ✅ Checkout API
14. ✅ Payment Processing API

### Phase 5 - Discussions (Week 7)
15. ✅ Course Discussion APIs

---

## 📝 IMPLEMENTATION NOTES

### General Patterns to Follow:

1. **Use Django REST Framework ViewSets or APIView**
   - Consistent with existing `api/views/*.py` structure
   - Follow patterns from `api/views/courses.py` and `api/views/forum.py`

2. **Permission Classes**
   - Use `IsAuthenticated` for user-specific endpoints
   - Create custom permissions for teacher/admin-only endpoints
   - Example: `IsTeacherOrAdmin`, `IsTeacherOfCourse`, `IsAdminUser`

3. **Response Format**
   - Match existing API response format
   - Use `ApiResponse` wrapper for single objects
   - Use `PaginatedResponse` for lists

4. **Error Handling**
   - Return appropriate HTTP status codes
   - Provide clear error messages
   - Use Django REST Framework's exception handling

5. **File Uploads**
   - Use `MultiPartParser` and `FormParser`
   - Validate file types and sizes
   - Store files in appropriate media directories

6. **Testing**
   - Write unit tests for each API endpoint
   - Test authentication and permissions
   - Test edge cases and error conditions

---

## 🔗 RELATED DOCUMENTATION

- **API Documentation**: `BACKEND_API_DOCUMENTATION.md`
- **Integration Summary**: `FRONTEND_BACKEND_INTEGRATION_SUMMARY.md`
- **Existing Backend Views**: 
  - `backend/nmtsa_lms/student_dash/views.py`
  - `backend/nmtsa_lms/teacher_dash/views.py`
  - `backend/nmtsa_lms/admin_dash/views.py`

---

*Last Updated: 2025-10-11*
*Created by: GitHub Copilot*
