# OAuth Implementation Guide

## Overview
This LMS uses **frontend-only OAuth** where the frontend handles the OAuth flow and sends user data to the backend for account management.

## Architecture

### Frontend (React + TypeScript)
- Handles OAuth popup/redirect flows
- Decodes OAuth tokens (Google JWT)
- Extracts user information
- Sends user data to backend via API

### Backend (Django + DRF)
- Receives user data (email, name, picture)
- Creates or retrieves user account
- Generates JWT token for API authentication
- Returns user profile and token

## Supported Providers

### 1. Google OAuth
- **Library**: `@react-oauth/google` (v0.12.2)
- **Component**: `<GoogleLogin>`
- **Token**: JWT credential (decoded with `jwt-decode`)
- **User Info**: email, name, picture from JWT payload

### 2. Microsoft OAuth
- **Library**: `@azure/msal-react` (v3.0.20), `@azure/msal-browser` (v4.25.0)
- **Hook**: `useMsal()`
- **Token**: Access token via popup
- **User Info**: email, displayName from `response.account`

## Setup Instructions

### 1. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure OAuth consent screen
6. Set authorized JavaScript origins:
   - Development: `http://localhost:5173`
   - Production: `https://yourdomain.com`
7. Copy **Client ID**
8. Add to `.env` file:
   ```
   VITE_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   ```

### 2. Microsoft OAuth Setup

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Configure:
   - Name: NMTSA LMS
   - Supported account types: Accounts in any organizational directory and personal Microsoft accounts
   - Redirect URI: Single-page application (SPA)
     - Development: `http://localhost:5173`
     - Production: `https://yourdomain.com`
5. Copy **Application (client) ID**
6. Add to `.env` file:
   ```
   VITE_MICROSOFT_CLIENT_ID=your-client-id-here
   VITE_MICROSOFT_AUTHORITY=https://login.microsoftonline.com/common
   VITE_MICROSOFT_REDIRECT_URI=http://localhost:5173
   ```

### 3. Backend Environment (Optional)
The backend doesn't need OAuth credentials since it only receives user data.
However, you may want to whitelist allowed OAuth providers:
```
# .env (backend)
ALLOWED_OAUTH_PROVIDERS=google,microsoft
```

## API Endpoint

### POST `/api/auth/oauth/signin`

**Request Body:**
```json
{
  "provider": "google" | "microsoft",
  "email": "user@example.com",
  "name": "John Doe",
  "picture": "https://..." // Optional
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "is_active": true
  },
  "isNewUser": false
}
```

**Error Response (400):**
```json
{
  "message": "Provider, email, and name are required"
}
```

## Frontend Implementation

### Configuration (`src/config/oauth.ts`)
```typescript
export type OAuthProvider = "google" | "microsoft";

export const oauthConfig = {
  google: {
    clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID || "",
  },
  microsoft: {
    clientId: import.meta.env.VITE_MICROSOFT_CLIENT_ID || "",
    authority: import.meta.env.VITE_MICROSOFT_AUTHORITY || 
      "https://login.microsoftonline.com/common",
    redirectUri: import.meta.env.VITE_MICROSOFT_REDIRECT_URI || 
      window.location.origin,
  },
};
```

### Provider Wrapper (`src/provider.tsx`)
```typescript
import { GoogleOAuthProvider } from "@react-oauth/google";
import { MsalProvider, PublicClientApplication } from "@azure/msal-react";

const msalInstance = new PublicClientApplication({
  auth: {
    clientId: oauthConfig.microsoft.clientId,
    authority: oauthConfig.microsoft.authority,
    redirectUri: oauthConfig.microsoft.redirectUri,
  },
  cache: {
    cacheLocation: "localStorage",
    storeAuthStateInCookie: false,
  },
});

<GoogleOAuthProvider clientId={oauthConfig.google.clientId}>
  <MsalProvider instance={msalInstance}>
    <App />
  </MsalProvider>
</GoogleOAuthProvider>
```

### OAuth Handlers (Login/Register pages)

#### Google OAuth
```typescript
import { jwtDecode } from "jwt-decode";
import { GoogleLogin, CredentialResponse } from "@react-oauth/google";

const handleGoogleSuccess = async (response: CredentialResponse) => {
  if (!response.credential) return;
  
  const decoded: any = jwtDecode(response.credential);
  
  await handleOAuthSuccess(
    "google",
    decoded.email,
    decoded.name,
    decoded.picture
  );
};
```

#### Microsoft OAuth
```typescript
import { useMsal } from "@azure/msal-react";

const { instance } = useMsal();

const handleMicrosoftLogin = async () => {
  const response = await instance.loginPopup({
    scopes: ["user.read"],
    prompt: "select_account",
  });
  
  await handleOAuthSuccess(
    "microsoft",
    response.account.username,
    response.account.name || response.account.username,
    undefined
  );
};
```

#### Common Handler
```typescript
const handleOAuthSuccess = async (
  provider: OAuthProvider,
  email: string,
  name: string,
  picture?: string
) => {
  setIsLoading(true);
  try {
    const result = await authService.oauthSignIn({
      provider,
      email,
      name,
      picture,
    });
    
    if (result?.profile) {
      useAuthStore.getState().setUser(result.profile);
      navigate("/dashboard");
    }
  } catch (error: any) {
    toast.error(error.response?.data?.message || "OAuth sign-in failed");
  } finally {
    setIsLoading(false);
  }
};
```

## Backend Implementation

### View (`api/views/auth.py`)
```python
class OAuthSignInView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        provider = request.data.get('provider')
        email = request.data.get('email')
        name = request.data.get('name')
        picture = request.data.get('picture')
        
        if not provider or not email or not name:
            return Response(
                {'message': 'Provider, email, and name are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': name.split()[0] if ' ' in name else name,
                'last_name': ' '.join(name.split()[1:]) if ' ' in name else '',
                'role': 'student',
                'is_active': True,
            }
        )
        
        # Update profile picture if provided
        if picture and not user.profile_picture:
            user.profile_picture = picture
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login', 'profile_picture'] if picture else ['last_login'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'token': str(refresh.access_token),
            'refreshToken': str(refresh),
            'user': UserSerializer(user).data,
            'isNewUser': created
        })
```

## Security Considerations

### Frontend
1. **Token Validation**: Google JWT tokens are decoded locally (no signature verification needed since we send data to our backend anyway)
2. **HTTPS Only**: In production, always use HTTPS to protect OAuth flows
3. **CSRF Protection**: OAuth popup prevents CSRF attacks
4. **Storage**: Tokens stored in localStorage (consider httpOnly cookies for production)

### Backend
1. **Email Uniqueness**: Email is used as unique identifier
2. **JWT Tokens**: Backend generates its own JWT tokens (not OAuth tokens)
3. **User Verification**: Backend trusts frontend to verify OAuth providers
4. **Rate Limiting**: Consider adding rate limiting to OAuth endpoint

## Testing

### Manual Testing
1. Start frontend: `cd frontend && npm run dev`
2. Start backend: `cd backend/nmtsa_lms && python manage.py runserver`
3. Navigate to `http://localhost:5173/login`
4. Click Google or Microsoft OAuth button
5. Complete OAuth flow in popup
6. Verify redirect to `/dashboard`
7. Check network tab for API calls
8. Verify JWT token in localStorage

### Edge Cases to Test
- [ ] User already exists with email
- [ ] User provides incomplete OAuth data
- [ ] Network failure during OAuth
- [ ] Token expiration
- [ ] Duplicate login attempts
- [ ] Profile picture URL handling

## Troubleshooting

### Google OAuth Issues
- **"redirect_uri_mismatch"**: Update authorized origins in Google Console
- **"popup_closed_by_user"**: User closed popup, handle gracefully
- **"invalid_client"**: Check VITE_GOOGLE_CLIENT_ID environment variable

### Microsoft OAuth Issues
- **"AADSTS50011: Redirect URI mismatch"**: Update redirect URI in Azure Portal
- **"AADSTS65004: User declined consent"**: User needs to accept permissions
- **"Network error"**: Check CORS settings and network connectivity

### Backend Issues
- **400 "Provider, email, and name are required"**: Frontend not sending complete data
- **500 Internal Server Error**: Check Django logs for details
- **Token not generated**: Check JWT settings in `settings.py`

## Future Enhancements

1. **Add more providers**: Facebook, Apple, GitHub, LinkedIn
2. **Profile picture sync**: Download and store OAuth profile pictures locally
3. **Account linking**: Allow users to link multiple OAuth providers
4. **Role detection**: Auto-assign roles based on email domain
5. **Admin approval**: Require admin approval for new OAuth sign-ups
6. **Audit logging**: Log all OAuth sign-ins for security monitoring

## References

- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Microsoft MSAL Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/msal-overview)
- [@react-oauth/google](https://www.npmjs.com/package/@react-oauth/google)
- [@azure/msal-react](https://www.npmjs.com/package/@azure/msal-react)
- [Django REST Framework JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
