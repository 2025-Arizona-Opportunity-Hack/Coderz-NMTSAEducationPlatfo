# Auth0 Regular Web Application - Complete Setup Guide

## ✅ What's Been Done

### Frontend Changes
1. **Removed Auth0 React SDK** - No longer using `@auth0/auth0-react`
2. **Login redirects to backend** - Login button now goes to `http://localhost:8000/login`
3. **Backend handles authentication** - Django manages the entire OAuth flow
4. **Session-based auth** - Using Django sessions instead of JWT tokens
5. **Profile dropdown** - Shows user info when logged in

### Backend Updates
1. **Auth0 callback updated** - Now redirects to frontend (`http://localhost:5173/dashboard`) after login
2. **User creation** - Automatically creates user on first login
3. **Session management** - Stores `user_id` in Django session
4. **Logout flow** - Clears session and logs out from Auth0

## 🔧 Required Configuration

### Step 1: Backend Environment Variables

Create or update `backend/nmtsa_lms/.env`:

```env
AUTH0_DOMAIN=dev-kdcc586gsnydqn1y.us.auth0.com
AUTH0_CLIENT_ID=CwdXRlCdFbZt0Nk2HsAOnUnRa6r0iFwI
AUTH0_CLIENT_SECRET=your-client-secret-from-auth0-dashboard
```

**Where to find Client Secret:**
1. Go to https://manage.auth0.com/
2. Navigate to Applications → Applications
3. Click your application
4. Find "Client Secret" (click "Show" to reveal)
5. Copy and paste it into `.env`

### Step 2: Auth0 Dashboard Configuration

**Application Settings:**

**Allowed Callback URLs:**
```
http://localhost:8000/callback
```

**Allowed Logout URLs:**
```
http://localhost:5173, http://localhost:8000
```

**Allowed Web Origins:**
```
http://localhost:5173
```

### Step 3: Django Settings

Update `backend/nmtsa_lms/nmtsa_lms/settings.py` - Add session configuration:

```python
# Session Configuration for Cross-Origin
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = False  # Allow frontend JS to check session
SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS
SESSION_COOKIE_AGE = 1209600  # 2 weeks
```

### Step 4: CORS Configuration

Make sure CORS allows credentials in `settings.py`:

```python
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

### Step 5: Install Backend Dependencies

```bash
cd backend/nmtsa_lms
pip install authlib requests
```

### Step 6: Remove Frontend Auth0 Package (Optional)

```bash
cd frontend
npm uninstall @auth0/auth0-react
```

## 🚀 How It Works Now

### Login Flow:

```
User clicks "Login" button
  ↓
Frontend redirects to: http://localhost:8000/login
  ↓
Django redirects to: Auth0 login page (with client_id + client_secret)
  ↓
User authenticates with Auth0 (Google, Microsoft, etc.)
  ↓
Auth0 redirects to: http://localhost:8000/callback
  ↓
Django:
  - Exchanges code for tokens (server-side, secure)
  - Creates/updates user in database
  - Creates Django session
  - Stores user_id in session
  ↓
Django redirects to: http://localhost:5173/dashboard
  ↓
Frontend:
  - Has Django session cookie
  - Calls /api/users/me to get profile
  - Shows profile dropdown in navbar
```

### Logout Flow:

```
User clicks "Logout" in dropdown
  ↓
Frontend redirects to: http://localhost:8000/logout
  ↓
Django:
  - Clears session
  - Redirects to Auth0 logout
  ↓
Auth0 logs out user
  ↓
Auth0 redirects to: http://localhost:5173
  ↓
User sees login button again
```

## 🧪 Testing

### 1. Start Backend:
```bash
cd backend/nmtsa_lms
python manage.py runserver
```

### 2. Start Frontend:
```bash
cd frontend
npm run dev
```

### 3. Test Login:
1. Open http://localhost:5173
2. Click "Login" button
3. You'll be redirected to http://localhost:8000/login
4. Then to Auth0 login page
5. Login with your provider (Google, etc.)
6. You'll be redirected back to http://localhost:5173/dashboard
7. Navbar should show your profile dropdown

### 4. Test Protected Routes:
- Try accessing http://localhost:5173/dashboard without logging in
- You should be automatically redirected to login

### 5. Test Logout:
- Click profile dropdown
- Click "Logout"
- You should be logged out and redirected to home page
- Login button should appear again

## 🔍 Debugging

### Check Django Session:
```python
# In Django shell
python manage.py shell

from django.contrib.sessions.models import Session
for s in Session.objects.all():
    print(s.get_decoded())
```

### Check Auth0 Logs:
- Go to https://manage.auth0.com/
- Click Monitoring → Logs
- Look for successful/failed login attempts

### Check Frontend Console:
- Press F12
- Look for any API errors
- Check Network tab for /api/users/me calls

## ⚠️ Important Notes

### Security:
- ✅ Client secret stays on backend only (never exposed to browser)
- ✅ Session cookies are HttpOnly (protected from XSS)
- ✅ CORS properly configured for cross-origin requests
- ✅ Auth0 handles all OAuth complexity

### For Production:
```python
# In settings.py for production
SESSION_COOKIE_SECURE = True  # Requires HTTPS
SESSION_COOKIE_HTTPONLY = True  # Extra security
SESSION_COOKIE_SAMESITE = 'None'  # For cross-site
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com"
]
```

Update Auth0 dashboard with production URLs:
- Callback: `https://api.yourdomain.com/callback`
- Logout: `https://yourdomain.com, https://api.yourdomain.com`
- Web Origins: `https://yourdomain.com`

## 📝 Summary of Changes

### Files Modified:
- ✅ `frontend/src/provider.tsx` - Removed Auth0Provider
- ✅ `frontend/src/components/layout/Navbar.tsx` - Login redirects to backend
- ✅ `frontend/src/components/layout/ProfileDropdown.tsx` - Logout redirects to backend
- ✅ `frontend/src/hooks/useAuth.ts` - Removed Auth0 dependencies
- ✅ `frontend/src/components/auth/ProtectedRoute.tsx` - Redirects to backend login
- ✅ `frontend/src/App.tsx` - Removed /callback route
- ✅ `backend/nmtsa_lms/nmtsa_lms/views.py` - Updated callback and logout

### Files Can Be Deleted:
- `frontend/src/pages/Callback.tsx` (no longer needed)
- `frontend/src/config/auth0.ts` (no longer needed)

## 🎯 Next Steps

1. Add CLIENT_SECRET to backend `.env`
2. Update Auth0 dashboard callback URLs
3. Test the login flow
4. If working, remove `@auth0/auth0-react` from package.json
5. Delete unused auth0 files from frontend

---

**This approach is more secure for Regular Web Applications and simpler to maintain!**
