# Regular Web Application Auth0 Integration

## Architecture Overview

For **Regular Web Applications**, authentication happens on the **backend** (Django), not the frontend (React).

### Current Setup
✅ Backend Auth0 already configured in `backend/nmtsa_lms/nmtsa_lms/views.py`
✅ Django handles OAuth flow with client secret
✅ Sessions stored server-side

### What Needs to Change

#### ❌ Remove (Frontend Auth0 SDK)
- `@auth0/auth0-react` package
- Frontend auth0 config
- Auth0Provider in provider.tsx
- Frontend callback handling

#### ✅ Add (Backend-Driven Auth)
- Frontend redirects to Django `/login` endpoint
- Django handles Auth0 OAuth flow
- Django callback creates session
- Django redirects back to frontend with session cookie
- Frontend checks backend for auth status

## Implementation Steps

### Step 1: Update Frontend to Use Backend Auth

**Flow:**
```
User clicks Login 
  → Frontend redirects to: http://localhost:8000/login
  → Django redirects to: Auth0 login page
  → User authenticates
  → Auth0 redirects to: http://localhost:8000/callback
  → Django creates session
  → Django redirects to: http://localhost:5173/dashboard (frontend)
  → Frontend uses session cookie for API calls
```

### Step 2: Backend Configuration

Add to `backend/nmtsa_lms/.env`:
```env
AUTH0_DOMAIN=dev-kdcc586gsnydqn1y.us.auth0.com
AUTH0_CLIENT_ID=CwdXRlCdFbZt0Nk2HsAOnUnRa6r0iFwI
AUTH0_CLIENT_SECRET=your-client-secret-here
```

### Step 3: Auth0 Dashboard Configuration

For Regular Web Application, configure:

**Allowed Callback URLs:**
```
http://localhost:8000/callback
```

**Allowed Logout URLs:**
```
http://localhost:8000, http://localhost:5173
```

**Allowed Web Origins:**
```
http://localhost:5173
```

### Step 4: Session Cookie Configuration

Django needs to send session cookies that frontend can use:

```python
# In settings.py
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = False  # Allow frontend JS to check if logged in
SESSION_COOKIE_SECURE = False  # True in production with HTTPS
SESSION_COOKIE_DOMAIN = None  # None for localhost
```

## Advantages of This Approach

✅ **Secure**: Client secret stays on backend only
✅ **Simple**: No token management in frontend  
✅ **Standard**: Uses Django session authentication
✅ **Compatible**: Works with Regular Web Application type

## Next Steps

1. Remove frontend Auth0 SDK
2. Update frontend to redirect to backend `/login`
3. Configure Django session cookies
4. Update backend to redirect back to frontend after login
5. Add session check endpoint for frontend

Would you like me to implement this approach?
