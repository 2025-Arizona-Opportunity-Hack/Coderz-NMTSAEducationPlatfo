# Setup & Deployment Checklist

## 🎯 Current Status

### ✅ Completed
- [x] Forum API implementation (ForumPost, ForumComment, ForumLike models)
- [x] OAuth frontend implementation (Google + Microsoft)
- [x] OAuth backend endpoint simplified (receives user data only)
- [x] Removed unnecessary OAuth validation libraries
- [x] Updated Login.tsx and Register.tsx with OAuth buttons
- [x] Fixed infinite API loops in Explore.tsx and Forum.tsx
- [x] Created OAuth documentation (OAUTH_IMPLEMENTATION.md)

### ⚠️ Pending
- [ ] Run database migrations for forum models
- [ ] Configure OAuth provider credentials
- [ ] Test OAuth flow end-to-end
- [ ] Configure environment variables

---

## 🚀 Quick Start (Development)

### 1. Backend Setup

```bash
cd backend/nmtsa_lms

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Run migrations (including new forum models)
python manage.py makemigrations lms
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Backend will be available at: `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
# or: pnpm install

# Copy environment variables
cp .env.example .env

# Edit .env and add OAuth credentials (see step 3)
nano .env

# Run development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### 3. Configure OAuth Providers

#### Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Google+ API
3. Create OAuth 2.0 Client ID
4. Add authorized JavaScript origins:
   - `http://localhost:5173`
   - `http://localhost:5174` (if running multiple instances)
5. Copy Client ID to `.env`:
   ```
   VITE_GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
   ```

#### Microsoft OAuth
1. Go to [Azure Portal](https://portal.azure.com/)
2. Azure AD → App registrations → New registration
3. Set redirect URI: `http://localhost:5173` (SPA type)
4. Copy Application ID to `.env`:
   ```
   VITE_MICROSOFT_CLIENT_ID=your-microsoft-client-id
   VITE_MICROSOFT_AUTHORITY=https://login.microsoftonline.com/common
   VITE_MICROSOFT_REDIRECT_URI=http://localhost:5173
   ```

---

## 📋 Database Migrations

### Forum Models Migration

The forum functionality requires new database tables:

```bash
cd backend/nmtsa_lms

# Generate migrations
python manage.py makemigrations lms

# Expected output:
# Migrations for 'lms':
#   lms/migrations/0003_forumpost_forumcomment_forumlike.py
#     - Create model ForumPost
#     - Create model ForumComment
#     - Create model ForumLike
#     - Add constraint forumlike_unique_post_like
#     - Add constraint forumlike_unique_comment_like

# Apply migrations
python manage.py migrate

# Expected output:
# Running migrations:
#   Applying lms.0003_forumpost_forumcomment_forumlike... OK
```

### Verify Migration Success

```bash
# Check migration status
python manage.py showmigrations lms

# Expected output:
# lms
#  [X] 0001_initial
#  [X] 0002_videoprogress
#  [X] 0003_forumpost_forumcomment_forumlike

# Test in Django shell
python manage.py shell

>>> from lms.models import ForumPost, ForumComment, ForumLike
>>> ForumPost.objects.count()
0
>>> # Success! Models are accessible
```

---

## 🧪 Testing OAuth Flow

### Manual Testing Steps

1. **Start both servers:**
   ```bash
   # Terminal 1 - Backend
   cd backend/nmtsa_lms
   python manage.py runserver

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

2. **Test Google OAuth:**
   - Navigate to `http://localhost:5173/login`
   - Click "Sign in with Google"
   - Verify popup opens
   - Select Google account
   - Check:
     - [ ] Popup closes
     - [ ] Redirects to `/dashboard`
     - [ ] JWT token in localStorage (`auth-token`)
     - [ ] User profile loaded in UI
   - Check browser console for errors
   - Check Network tab for API calls:
     - [ ] POST `/api/auth/oauth/signin` returns 200
     - [ ] Response has `token`, `user`, `isNewUser`

3. **Test Microsoft OAuth:**
   - Navigate to `http://localhost:5173/login`
   - Click "Sign in with Microsoft"
   - Verify popup opens
   - Select Microsoft account
   - Accept permissions
   - Same checks as Google

4. **Test Registration:**
   - Navigate to `http://localhost:5173/register`
   - Repeat OAuth tests
   - Verify `isNewUser: true` in response

### Backend Testing

```bash
# Test OAuth endpoint directly
curl -X POST http://localhost:8000/api/auth/oauth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "google",
    "email": "test@example.com",
    "name": "Test User",
    "picture": "https://example.com/pic.jpg"
  }'

# Expected response:
# {
#   "token": "eyJhbGciOiJIUzI1NiIs...",
#   "refreshToken": "eyJhbGciOiJIUzI1NiIs...",
#   "user": {
#     "id": 1,
#     "email": "test@example.com",
#     "username": "test",
#     "first_name": "Test",
#     "last_name": "User",
#     "role": "student",
#     "is_active": true
#   },
#   "isNewUser": true
# }
```

### Forum API Testing

```bash
# Test forum posts endpoint
curl http://localhost:8000/api/forum/posts

# Expected response:
# {
#   "count": 0,
#   "next": null,
#   "previous": null,
#   "results": []
# }

# Test forum tags endpoint
curl http://localhost:8000/api/forum/tags

# Expected response:
# []
```

---

## 🔧 Troubleshooting

### OAuth Issues

#### "redirect_uri_mismatch" (Google)
```bash
# Check configured origins in Google Console
# Must exactly match: http://localhost:5173

# Check .env file
cat frontend/.env | grep GOOGLE
```

#### "AADSTS50011: Redirect URI mismatch" (Microsoft)
```bash
# Check Azure Portal redirect URIs
# Must be SPA type, not Web

# Check .env file
cat frontend/.env | grep MICROSOFT
```

#### "popup_closed_by_user"
- User manually closed popup
- Handle gracefully in UI (already implemented)

#### "Token not saved" or "Not redirecting"
```javascript
// Check browser console
// Verify localStorage has 'auth-token'
localStorage.getItem('auth-token')

// Check Network tab
// Look for 200 response from /api/auth/oauth/signin
```

### Database Issues

#### "relation does not exist"
```bash
# Migrations not applied
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

#### "UNIQUE constraint failed"
```bash
# User with email already exists
# This is expected - OAuth will find existing user

# To reset (development only):
python manage.py flush
```

### API Issues

#### "CORS error"
```python
# Check backend/nmtsa_lms/nmtsa_lms/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
]
```

#### "404 Not Found: /api/auth/oauth/signin"
```python
# Check backend/nmtsa_lms/api/urls.py
urlpatterns = [
    path('auth/oauth/signin', OAuthSignInView.as_view(), name='oauth-signin'),
    # ...
]
```

---

## 📦 Production Deployment

### Environment Variables

#### Frontend (.env.production)
```bash
VITE_API_BASE_URL=https://api.yourdomain.com/api
VITE_APP_URL=https://yourdomain.com

# Google OAuth (update authorized origins)
VITE_GOOGLE_CLIENT_ID=your-production-client-id

# Microsoft OAuth (update redirect URIs)
VITE_MICROSOFT_CLIENT_ID=your-production-client-id
VITE_MICROSOFT_AUTHORITY=https://login.microsoftonline.com/common
VITE_MICROSOFT_REDIRECT_URI=https://yourdomain.com
```

#### Backend (backend/.env)
```bash
DEBUG=False
SECRET_KEY=generate-strong-secret-key
ALLOWED_HOSTS=api.yourdomain.com,yourdomain.com

DATABASE_URL=postgresql://user:password@localhost/dbname
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# JWT Settings
SIMPLE_JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
SIMPLE_JWT_REFRESH_TOKEN_LIFETIME=1440  # 24 hours
```

### OAuth Provider Configuration

#### Google
1. Add production origin: `https://yourdomain.com`
2. Add production API: `https://api.yourdomain.com`
3. Verify domain ownership
4. Update consent screen

#### Microsoft
1. Add production redirect URI: `https://yourdomain.com`
2. Add Web API permissions if needed
3. Submit for verification if required

### Database

```bash
# Use PostgreSQL in production
pip install psycopg2-binary

# Update DATABASE_URL in .env
# Run migrations on production database
python manage.py migrate --settings=nmtsa_lms.settings_production
```

### Static Files

```bash
# Collect static files
python manage.py collectstatic --noinput

# Use whitenoise for serving
pip install whitenoise
```

---

## 🎓 Next Steps

### Immediate (Required)
1. [ ] Run `python manage.py makemigrations lms`
2. [ ] Run `python manage.py migrate`
3. [ ] Configure OAuth credentials in `.env`
4. [ ] Test OAuth login flow
5. [ ] Create test forum posts in admin

### Short Term (Recommended)
1. [ ] Add loading states for OAuth buttons
2. [ ] Add error handling for network failures
3. [ ] Implement token refresh logic
4. [ ] Add role-based redirects (admin → /admin-dash)
5. [ ] Test forum functionality (create posts, comments, likes)

### Long Term (Nice to Have)
1. [ ] Add more OAuth providers (Facebook, GitHub)
2. [ ] Implement account linking (multiple OAuth providers)
3. [ ] Add profile picture upload
4. [ ] Implement email verification
5. [ ] Add rate limiting to OAuth endpoint
6. [ ] Set up monitoring and logging

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Google OAuth Guide](https://developers.google.com/identity/protocols/oauth2)
- [Microsoft MSAL Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/msal-overview)

## 📖 Project Documentation

- `backend/OAUTH_IMPLEMENTATION.md` - Detailed OAuth implementation guide
- `backend/AUTH_SYSTEM_SUMMARY.md` - Authentication system overview
- `backend/AUTHENTICATION_COMPLETE.md` - Authentication completion status
- `backend/FRONTEND_DOCUMENTATION.md` - Frontend architecture
- `backend/QUICK_START.md` - Quick start guide
- `frontend/docs/PROJECT_SUMMARY.md` - Frontend project summary
- `frontend/docs/DEPLOYMENT.md` - Deployment guide

---

## 🐛 Known Issues

None at this time! 🎉

If you encounter any issues, check the troubleshooting section above or refer to the documentation.
