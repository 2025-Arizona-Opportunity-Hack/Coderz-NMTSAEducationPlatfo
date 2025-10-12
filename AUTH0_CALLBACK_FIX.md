# Auth0 Configuration Fix - 401 Unauthorized Error

## Problem
Getting 401 Unauthorized error during Auth0 callback because the callback URL doesn't match what's configured in Auth0 dashboard.

## Solution

### Step 1: Update Auth0 Dashboard Settings

1. Go to https://manage.auth0.com/
2. Navigate to **Applications** > **Applications**
3. Click on your application: **CwdXRlCdFbZt0Nk2HsAOnUnRa6r0iFwI**
4. Scroll to **Application URIs** section

### Step 2: Add These Exact URLs

**Allowed Callback URLs:**
```
http://localhost:5173/callback
```

**Allowed Logout URLs:**
```
http://localhost:5173
```

**Allowed Web Origins:**
```
http://localhost:5173
```

### Step 3: Important Notes

⚠️ **CRITICAL**: The URLs must match **EXACTLY**:
- Include the `/callback` path for callback URLs
- Use `http://` not `https://` for localhost
- No trailing slashes
- Port must match (5173)

### Step 4: Save and Test

1. Click **Save Changes** at the bottom of the Auth0 settings page
2. Wait 30 seconds for changes to propagate
3. Clear your browser cache or open an incognito window
4. Try logging in again

### Current Configuration

Your app is configured to use:
- **Callback URL**: `http://localhost:5173/callback`
- **Logout URL**: `http://localhost:5173`
- **Auth0 Domain**: `dev-kdcc586gsnydqn1y.us.auth0.com`
- **Client ID**: `CwdXRlCdFbZt0Nk2HsAOnUnRa6r0iFwI`

### Debugging

If you still get 401 errors after updating Auth0:

1. Check browser console for the exact redirect_uri being sent
2. Verify it matches what you added in Auth0 dashboard
3. Try logging out completely and clearing all Auth0 sessions
4. Check that your Auth0 application type is set to "Single Page Application"

### Common Mistakes

❌ **Wrong**: `http://localhost:5173` (missing /callback)
❌ **Wrong**: `http://localhost:5173/callback/` (trailing slash)
❌ **Wrong**: `https://localhost:5173/callback` (https instead of http)
✅ **Correct**: `http://localhost:5173/callback`

## Verification Steps

After configuring Auth0:

1. Open browser DevTools (F12)
2. Go to Network tab
3. Click Login button
4. Check the Auth0 authorize request
5. Look for `redirect_uri` parameter
6. Verify it matches: `http://localhost:5173/callback`

If it matches and you still get 401, the issue might be:
- Auth0 application is not a Single Page Application type
- Social connections are not enabled in Auth0
- Auth0 account has restrictions
