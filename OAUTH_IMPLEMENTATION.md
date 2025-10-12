# OAuth Authentication Implementation

## Overview

The NMTSA LMS now uses **OAuth-based authentication** for students and teachers. Username/password authentication is only available for admin users via the `/admin/login` page.

## Supported OAuth Providers

✅ **Google** - Sign in with Google account  
✅ **Microsoft** - Sign in with Microsoft account  
✅ **Facebook** - Sign in with Facebook account  
⏳ **Apple** - Coming soon (requires additional setup)

## Frontend Changes

### 1. Removed Features
- ❌ Email/password login form
- ❌ Registration form with username/password
- ❌ Forgot password functionality

### 2. New Components
- `OAuthButton.tsx` - Reusable OAuth provider button component
- OAuth configuration in `config/oauth.ts`
- OAuth providers wrapped in `provider.tsx`

### 3. Updated Pages
- **Login.tsx** - Now shows OAuth buttons only
- **Register.tsx** - Now shows OAuth buttons for signup
- **AdminLogin.tsx** - Separate page for admin username/password login

### 4. Dependencies Added
```json
{
  "@react-oauth/google": "^0.12.2",
  "@azure/msal-react": "^3.0.20",
  "@azure/msal-browser": "^4.25.0",
  "react-facebook-login": "^4.1.1"
}
```

## Backend Changes

### 1. New API Endpoint
```
POST /api/auth/oauth/signin
```

**Request Body:**
```json
{
  "provider": "google|facebook|microsoft|apple",
  "accessToken": "oauth-access-token",
  "idToken": "oauth-id-token",      // Optional
  "email": "user@example.com",      // Optional
  "name": "Full Name"               // Optional
}
```

**Response:**
```json
{
  "token": "jwt-access-token",
  "refreshToken": "jwt-refresh-token",
  "user": {
    "id": "1",
    "email": "user@example.com",
    "fullName": "Full Name",
    "role": "student",
    "avatarUrl": null,
    "createdAt": "2025-10-11T...",
    "updatedAt": "2025-10-11T..."
  },
  "isNewUser": true
}
```

### 2. Token Validation
The backend validates OAuth tokens with each provider's API:

- **Google**: Validates ID token with Google's public keys
- **Facebook**: Validates access token with Facebook Graph API
- **Microsoft**: Validates access token with Microsoft Graph API
- **Apple**: Validates ID token (requires additional setup)

### 3. User Creation
When a user signs in with OAuth for the first time:
- A new User account is created automatically
- Default role is set to "student"
- Email from OAuth provider is used as the unique identifier
- User is marked as active

### 4. Dependencies Added
```
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
PyJWT>=2.8.0
```

## Configuration

### Frontend Environment Variables

Create a `.env` file in the `frontend/` directory:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_URL=http://localhost:5173

# Google OAuth
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# Microsoft OAuth
VITE_MICROSOFT_CLIENT_ID=your-microsoft-client-id

# Facebook OAuth
VITE_FACEBOOK_APP_ID=your-facebook-app-id

# Apple OAuth (optional)
VITE_APPLE_CLIENT_ID=your-apple-client-id
```

### Backend Environment Variables

Create/update `.env` file in the `backend/` directory:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

## Setup Instructions

### 1. Install Dependencies

**Frontend:**
```bash
cd frontend
pnpm install
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure OAuth Providers

#### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Google+ API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Add authorized JavaScript origins:
   - `http://localhost:5173`
   - Your production domain
6. Add authorized redirect URIs:
   - `http://localhost:5173`
   - Your production domain
7. Copy the **Client ID** to `.env` files

#### Microsoft OAuth Setup
1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Add redirect URIs:
   - `http://localhost:5173`
   - Your production domain
5. Go to "API permissions" → Add "User.Read" permission
6. Copy the **Application (client) ID** to `.env` files

#### Facebook OAuth Setup
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app or select existing
3. Add "Facebook Login" product
4. Configure OAuth redirect URIs:
   - `http://localhost:5173`
   - Your production domain
5. Copy the **App ID** to `.env` files

### 3. Run the Application

**Backend:**
```bash
cd backend/nmtsa_lms
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
pnpm dev
```

### 4. Test OAuth Login

1. Navigate to `http://localhost:5173/login`
2. Click on any OAuth provider button
3. Complete the OAuth flow
4. You should be redirected to the dashboard

## Authentication Flow

```
┌─────────┐                 ┌──────────┐                 ┌─────────┐
│ Browser │                 │ Frontend │                 │ Backend │
└────┬────┘                 └────┬─────┘                 └────┬────┘
     │                           │                            │
     │ 1. Click "Sign in"        │                            │
     ├──────────────────────────>│                            │
     │                           │                            │
     │ 2. Redirect to OAuth      │                            │
     │    provider               │                            │
     ├──────────────────────────>│                            │
     │                           │                            │
     │ 3. Complete OAuth flow    │                            │
     │    (user authorizes)      │                            │
     │<──────────────────────────┤                            │
     │                           │                            │
     │ 4. Receive OAuth token    │                            │
     │<──────────────────────────┤                            │
     │                           │                            │
     │                           │ 5. POST /api/auth/oauth    │
     │                           ├───────────────────────────>│
     │                           │    {provider, accessToken} │
     │                           │                            │
     │                           │ 6. Validate token with     │
     │                           │    OAuth provider API      │
     │                           │                            │
     │                           │ 7. Create/update user      │
     │                           │                            │
     │                           │ 8. Generate JWT token      │
     │                           │<───────────────────────────┤
     │                           │    {token, user}           │
     │                           │                            │
     │ 9. Store JWT in localStorage                          │
     │<──────────────────────────┤                            │
     │                           │                            │
     │ 10. Navigate to dashboard │                            │
     ├──────────────────────────>│                            │
```

## API Endpoints

### User Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/oauth/signin` | OAuth sign in | No |
| POST | `/api/auth/admin/login` | Admin login | No |
| GET | `/api/auth/me` | Get current user | Yes |
| POST | `/api/auth/logout` | Logout | Yes |
| POST | `/api/auth/token/refresh` | Refresh JWT | Yes |

## Security Considerations

### Token Validation
- OAuth tokens are validated with provider APIs before creating user sessions
- Expired tokens are rejected
- Invalid tokens return 401 Unauthorized

### JWT Tokens
- JWT tokens are used for API authentication after OAuth validation
- Tokens are stored in localStorage
- Tokens expire after a configured duration
- Refresh tokens allow obtaining new access tokens

### CORS Configuration
- Backend CORS is configured to allow requests from frontend origin
- Only specified origins are allowed in production

### User Privacy
- OAuth providers only share email and name
- No passwords are stored in the database
- User data from OAuth providers is not stored unnecessarily

## Troubleshooting

### "OAuth provider not configured"
- Ensure environment variables are set correctly
- Check that client IDs match the OAuth provider console

### "Token validation failed"
- Verify that the OAuth provider's redirect URIs are configured correctly
- Check that the client ID matches between frontend and backend

### "CORS error"
- Ensure `CORS_ALLOWED_ORIGINS` in Django settings includes frontend URL
- Check that the frontend API base URL is correct

### "User not found" after OAuth
- Backend should create users automatically on first OAuth sign-in
- Check database for user creation errors

## Migration from Password Authentication

If you have existing users with password authentication:

1. Users can no longer log in with passwords
2. They must use OAuth providers
3. Email matching is used to link OAuth accounts to existing users
4. Admin users still use username/password via `/admin/login`

## Next Steps

1. ✅ Configure OAuth providers
2. ✅ Test OAuth login flow
3. ⏳ Set up Apple Sign In (requires Apple Developer account)
4. ⏳ Add profile picture support from OAuth providers
5. ⏳ Add account linking (multiple OAuth providers for one user)
6. ⏳ Add two-factor authentication for admin accounts
