# Auth0 Setup - Quick Start Guide

## Prerequisites
- Auth0 account (free tier works fine)
- Node.js and npm installed
- Frontend dependencies installed

## Step 1: Create Auth0 Application

1. Go to [Auth0 Dashboard](https://manage.auth0.com/)
2. Click **Applications** → **Create Application**
3. Name: `NMTSA Learn` (or your preferred name)
4. Type: **Single Page Web Applications**
5. Click **Create**

## Step 2: Configure Application Settings

In your Auth0 application settings:

### Allowed Callback URLs
```
http://localhost:5173, https://yourdomain.com
```

### Allowed Logout URLs
```
http://localhost:5173, https://yourdomain.com
```

### Allowed Web Origins
```
http://localhost:5173, https://yourdomain.com
```

### Allowed Origins (CORS)
```
http://localhost:5173, https://yourdomain.com
```

Click **Save Changes**

## Step 3: Configure Social Connections

1. Go to **Authentication** → **Social**
2. Enable the providers you want:

### Google
- Click the Google connection
- Enter your Google Client ID and Secret
- (Get these from [Google Cloud Console](https://console.cloud.google.com/))

### Microsoft
- Click the Microsoft connection  
- Enter your Microsoft Application ID and Secret
- (Get these from [Azure Portal](https://portal.azure.com/))

### Apple
- Click the Apple connection
- Configure Apple Sign In credentials
- (Get these from [Apple Developer Portal](https://developer.apple.com/))

### Facebook
- Click the Facebook connection
- Enter your Facebook App ID and Secret
- (Get these from [Facebook Developers](https://developers.facebook.com/))

## Step 4: Get Your Credentials

In your Auth0 application page:

1. **Domain**: Copy this (e.g., `your-tenant.us.auth0.com`)
2. **Client ID**: Copy this
3. **Client Secret**: ⚠️ **DO NOT USE IN FRONTEND** (only for backend if needed)

## Step 5: Update Environment Variables

### Frontend `.env` file:

```bash
# Auth0 Configuration
VITE_AUTH0_DOMAIN=your-tenant.us.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id-here

# OPTIONAL: Only if you have an Auth0 API configured
# VITE_AUTH0_AUDIENCE=https://your-api-identifier

# Backend API
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_URL=http://localhost:5173
```

**Important Notes:**
- ⚠️ **Never** add `VITE_AUTH0_CLIENT_SECRET` to frontend `.env`
- Client secrets are only for backend/confidential applications
- Frontend SPAs use PKCE flow which doesn't need secrets
- If you have `VITE_AUTH0_CLIENT_SECRET`, remove it!

## Step 6: Install Dependencies

```bash
cd frontend
npm install
```

The `@auth0/auth0-react` package should already be in `package.json`.

## Step 7: Test the Application

### Start Frontend:
```bash
cd frontend
npm run dev
```

### Visit:
```
http://localhost:5173/login
```

### Test Login Flow:
1. Click "Sign In" button
2. You'll be redirected to Auth0 Universal Login
3. Choose a social provider (Google, Microsoft, etc.)
4. Authenticate with that provider
5. You'll be redirected back to your app
6. Backend will exchange the Auth0 token for a JWT

## Step 8: Verify Backend Integration

Your backend needs to accept Auth0 tokens. Check that:

1. **OAuth endpoint exists**: `POST /api/auth/oauth/signin`
2. **Accepts `provider: "auth0"`**
3. **Validates Auth0 JWT tokens**
4. **Returns backend JWT token**

Example backend code needed:
```python
# In your auth view
if data.get('provider') == 'auth0':
    # Validate Auth0 token
    auth0_token = data.get('auth0Token')
    # Decode and verify the token
    # Create/update user
    # Return your backend JWT
```

## Troubleshooting

### "Access Denied" after login
- Check Allowed Callback URLs in Auth0 dashboard
- Verify the URL matches exactly (including protocol)

### "Invalid state" error  
- Clear browser cache and cookies
- Try in incognito mode
- Check that redirect URI is configured correctly

### Authentication loops
- Clear localStorage: `localStorage.clear()` in browser console
- Check that backend is accepting Auth0 tokens
- Verify environment variables are set correctly

### Backend not receiving tokens
- Check CORS settings in backend
- Verify API_BASE_URL in frontend `.env`
- Check browser network tab for API errors

### "Audience is required" error
- Either set `VITE_AUTH0_AUDIENCE` in `.env`
- Or remove the audience requirement from `auth0.ts`

## Testing Checklist

- [ ] Can access `/login` page
- [ ] Clicking "Sign In" redirects to Auth0
- [ ] Can see social provider buttons (Google, Microsoft, etc.)
- [ ] Can successfully authenticate with Google
- [ ] Gets redirected back to app after auth
- [ ] Backend receives and validates Auth0 token
- [ ] Backend returns JWT token
- [ ] Frontend stores JWT token
- [ ] Can access protected routes
- [ ] User profile loads correctly
- [ ] Logout works properly

## Additional Configuration (Optional)

### Customize Auth0 Universal Login
1. Go to **Branding** → **Universal Login**
2. Customize logo, colors, and text
3. Upload your company logo

### Add Custom Metadata
1. Go to **Actions** → **Flows** → **Login**
2. Create custom action to add user metadata
3. Add custom claims to tokens (e.g., user role)

### Enable MFA (Multi-Factor Authentication)
1. Go to **Security** → **Multi-factor Auth**
2. Enable desired MFA methods
3. Configure when MFA is required

## Support Resources

- [Auth0 Documentation](https://auth0.com/docs)
- [Auth0 React SDK](https://github.com/auth0/auth0-react)
- [Auth0 Community](https://community.auth0.com/)
- [Auth0 Support](https://support.auth0.com/)

## Security Best Practices

✅ **DO:**
- Keep Client ID in environment variables
- Use HTTPS in production
- Set proper CORS policies
- Validate tokens on backend
- Use refresh tokens
- Set token expiration times

❌ **DON'T:**
- Put Client Secret in frontend code
- Commit `.env` files to git
- Skip token validation on backend
- Use HTTP in production
- Store sensitive data in tokens
- Trust frontend-only authentication
