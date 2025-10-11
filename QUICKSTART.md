# 🎓 NMTSA LMS - Frontend-Backend Integration

## 📋 Overview

This document provides a **quick-start guide** for the integrated frontend-backend system. The NMTSA LMS now has a complete REST API that allows the React frontend to communicate with the Django backend.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
setup-integration.bat
```

**Mac/Linux:**
```bash
chmod +x setup-integration.sh
./setup-integration.sh
```

### Option 2: Manual Setup

#### 1. Install Backend Dependencies
```bash
cd backend/nmtsa_lms
pip install -e .  # or: uv sync
```

#### 2. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 3. Create Admin User
```bash
python manage.py shell < ../../create_admin.py
```

Or manually:
```python
python manage.py shell

from authentication.models import User
User.objects.create_user(
    username='admin',
    email='admin@example.com',
    password='admin123',
    role='admin',
    onboarding_complete=True
)
```

#### 4. Install Frontend Dependencies
```bash
cd frontend
npm install  # or: pnpm install
```

## 🏃 Running the Application

### Start Backend (Terminal 1)
```bash
cd backend/nmtsa_lms
python manage.py runserver
```
Backend runs on: http://localhost:8000

### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev  # or: pnpm dev
```
Frontend runs on: http://localhost:5173

## 🔐 Access Points

- **Frontend**: http://localhost:5173
- **Admin Login**: http://localhost:5173/admin-login
- **API Base**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin/

### Default Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`

## 📚 Documentation

- **[INTEGRATION_PLAN.md](./INTEGRATION_PLAN.md)** - Comprehensive integration guide
- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - What's been implemented
- **[AUTH_SYSTEM_SUMMARY.md](./backend/AUTH_SYSTEM_SUMMARY.md)** - Authentication system details

## 🎯 Key Features Implemented

### ✅ Authentication
- Admin login with username/password
- JWT token-based API authentication
- OAuth integration for students/teachers (existing)
- Separate admin login page

### ✅ Course Management
- List courses with search and filters
- Course details with modules and lessons
- Course enrollment/unenrollment
- Featured courses
- Categories

### ✅ Dashboard
- User statistics (enrollments, completions, learning hours)
- Enrollment list with progress
- Continue learning recommendations
- Certificates for completed courses

### ✅ API Infrastructure
- REST API with Django REST Framework
- JWT authentication
- CORS configuration
- Consistent response format
- Pagination support

## 🔧 API Endpoints

### Authentication
```
POST   /api/auth/admin/login      - Admin login
GET    /api/auth/me               - Get current user
POST   /api/auth/logout           - Logout
POST   /api/auth/token/refresh    - Refresh JWT token
```

### Courses
```
GET    /api/courses                     - List courses (with filters)
GET    /api/courses/{id}                - Course details
GET    /api/courses/{id}/detail         - Full course with modules
GET    /api/courses/categories          - List categories
GET    /api/courses/featured            - Featured courses
POST   /api/courses/{id}/enroll         - Enroll in course
DELETE /api/courses/{id}/enroll         - Unenroll from course
GET    /api/courses/{id}/reviews        - Course reviews
```

### Dashboard
```
GET    /api/dashboard/stats             - User statistics
GET    /api/dashboard/enrollments       - User enrollments
GET    /api/dashboard/continue-learning - Continue learning items
GET    /api/dashboard/certificates      - User certificates
```

## 🧪 Testing the Integration

### 1. Test API Directly
```bash
# Get courses (public)
curl http://localhost:8000/api/courses

# Admin login
curl -X POST http://localhost:8000/api/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get dashboard (with token)
curl http://localhost:8000/api/dashboard/stats \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 2. Test Frontend
1. Navigate to http://localhost:5173/admin-login
2. Login with admin/admin123
3. Check browser console for any errors
4. Verify JWT token in localStorage
5. Navigate to dashboard

### 3. Check for CORS Issues
- Open browser DevTools → Network tab
- Make API requests from frontend
- Look for CORS errors in console
- Verify response headers include CORS headers

## ⚠️ Common Issues & Solutions

### Backend Issues

**Import Errors:**
```bash
# Reinstall dependencies
pip install -e .
```

**Migration Errors:**
```bash
# Reset database (DEV ONLY!)
rm db.sqlite3
python manage.py migrate
```

**CORS Errors:**
- Check `CORS_ALLOWED_ORIGINS` in settings.py
- Ensure `corsheaders` is in INSTALLED_APPS
- Verify `CorsMiddleware` is first in MIDDLEWARE

### Frontend Issues

**API Connection Failed:**
- Verify backend is running on port 8000
- Check `VITE_API_BASE_URL` environment variable
- Look for network errors in browser console

**Authentication Issues:**
- Clear localStorage and try again
- Check if JWT token is being sent in headers
- Verify token hasn't expired

## 📊 Project Structure

```
nmstaeducationlms/
├── backend/
│   └── nmtsa_lms/
│       ├── api/                    # REST API app
│       │   ├── views/
│       │   │   ├── auth.py        # Auth endpoints
│       │   │   ├── courses.py     # Course endpoints
│       │   │   └── dashboard.py   # Dashboard endpoints
│       │   ├── serializers.py     # Model serializers
│       │   └── urls.py            # API routes
│       ├── authentication/         # User & auth models
│       ├── teacher_dash/          # Course models
│       ├── student_dash/          # Student views
│       ├── admin_dash/            # Admin views
│       └── nmtsa_lms/
│           └── settings.py        # Django settings
├── frontend/
│   └── src/
│       ├── pages/
│       │   └── AdminLogin.tsx     # Admin login page
│       ├── services/
│       │   ├── auth.service.ts    # Auth API calls
│       │   ├── course.service.ts  # Course API calls
│       │   └── dashboard.service.ts
│       └── config/
│           └── api.ts             # API configuration
├── INTEGRATION_PLAN.md            # Detailed integration guide
├── IMPLEMENTATION_SUMMARY.md       # Implementation checklist
├── setup-integration.sh           # Unix setup script
└── setup-integration.bat          # Windows setup script
```

## 🔄 Next Steps

1. **Test Integration**:
   - Run setup script
   - Start both servers
   - Test admin login
   - Test course browsing
   - Test enrollment

2. **Implement Remaining Features**:
   - Lesson content delivery API
   - Progress tracking API
   - Notes functionality
   - Forum/discussion API

3. **Production Preparation**:
   - Set up environment variables
   - Configure production database
   - Set up SSL/HTTPS
   - Deploy to production server

## 📝 Notes

- This is a **development setup**. Do NOT use these credentials in production!
- The integration uses JWT for API authentication and sessions for OAuth users
- Backend runs on port 8000, frontend on port 5173
- CORS is configured to allow requests from localhost:5173

## 🆘 Getting Help

If you encounter issues:

1. Check the logs (backend terminal and browser console)
2. Review the [INTEGRATION_PLAN.md](./INTEGRATION_PLAN.md)
3. Verify all dependencies are installed
4. Ensure migrations are applied
5. Check that CORS is properly configured

## 🎉 Success Criteria

The integration is working correctly when:

- ✅ No CORS errors in browser console
- ✅ Admin can login via AdminLogin page
- ✅ JWT token is stored in localStorage
- ✅ Dashboard shows correct statistics
- ✅ Courses can be browsed and filtered
- ✅ Enrollment works end-to-end
- ✅ API responses match frontend type expectations

---

**Happy Coding! 🚀**
