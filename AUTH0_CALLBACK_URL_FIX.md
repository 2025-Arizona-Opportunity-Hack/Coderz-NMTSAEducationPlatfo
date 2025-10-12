# Auth0 Callback URL Configuration Guide

## The Problem
You're getting this error:
```
Callback URL mismatch.
The provided redirect_uri is not in the list of allowed callback URLs.
```

## The Solution

### Step 1: Check Your Redirect URI

Your app is using: **`http://localhost:5173`**

This is configured in:
- `frontend/.env` → `VITE_APP_URL=http://localhost:5173`
- `frontend/src/config/auth0.ts` → uses `VITE_APP_URL` as `redirect_uri`

### Step 2: Update Auth0 Dashboard

1. Go to [Auth0 Dashboard](https://manage.auth0.com/)
2. Navigate to **Applications** → **Applications**
3. Click on your application (NMTSA Learn or whatever you named it)
4. Scroll to **Application URIs** section
5. Update these fields:

#### Allowed Callback URLs
```
http://localhost:5173
```
**Note:** No trailing slash, exact match required!

#### Allowed Logout URLs
```
http://localhost:5173
```

#### Allowed Web Origins
```
http://localhost:5173
```

#### Allowed Origins (CORS)
```
http://localhost:5173
```

6. Click **Save Changes** at the bottom

### Step 3: For Production

When you deploy to production, add your production URLs:

#### Allowed Callback URLs
```
http://localhost:5173, https://yourdomain.com
```

#### Allowed Logout URLs
```
http://localhost:5173, https://yourdomain.com
```

#### Allowed Web Origins
```
http://localhost:5173, https://yourdomain.com
```

## Common Mistakes

❌ **Wrong:**
- `http://localhost:5173/` (has trailing slash)
- `https://localhost:5173` (using https locally)
- `http://localhost:5173/login` (includes path)

✅ **Correct:**
- `http://localhost:5173` (exact match)

## Testing the Fix

1. Clear your browser cache and cookies
2. Go to `http://localhost:5173/dashboard` (or any protected page)
3. You should be automatically redirected to Auth0
4. After logging in, you should be redirected back successfully

## How the New Flow Works

### Before (with Login page):
1. User visits protected page → Redirects to `/login`
2. User clicks "Sign In" button → Goes to Auth0
3. Auth0 redirects back → Shows login page again
4. Login page exchanges token

### After (direct Auth0):
1. User visits protected page → **Automatically redirects to Auth0**
2. User logs in with Auth0 → Redirects back to app
3. App automatically exchanges token with backend
4. User is authenticated and can access protected pages

## No Login Page!

We've removed the `/login` page entirely. Now:
- Any protected route automatically redirects to Auth0
- Token exchange happens automatically in `useAuth` hook
- Users never see a "login" page in your app
- All authentication UI is handled by Auth0

## If You Still Get Errors

### Error: "Invalid state"
- Clear browser cache and localStorage
- Try in incognito mode
- Restart your dev server

### Error: Still callback mismatch
- Double-check Auth0 dashboard settings are saved
- Make sure `VITE_APP_URL` in `.env` matches Auth0 settings
- Restart your frontend dev server after changing `.env`

### Error: Redirect loop
- Check browser console for errors
- Verify backend is accepting Auth0 tokens
- Check that `auth0SignIn` method exists in auth.service.ts

## Environment Variables Checklist

Your `.env` should have:
```bash
VITE_APP_URL=http://localhost:5173
VITE_AUTH0_DOMAIN=dev-kdcc586gsnydqn1y.us.auth0.com
VITE_AUTH0_CLIENT_ID=CwdXRlCdFbZt0Nk2HsAOnUnRa6r0iFwI
```

**Do NOT include:**
- `VITE_AUTH0_CLIENT_SECRET` (not needed for SPAs!)
- `VITE_AUTH0_AUDIENCE` (optional, only if you have an Auth0 API)

## Files Changed

1. **`src/config/auth0.ts`**
   - Now uses `VITE_APP_URL` instead of `window.location.origin`
   - This ensures consistent redirect URI

2. **`src/components/auth/ProtectedRoute.tsx`**
   - Automatically triggers `loginWithRedirect()` when not authenticated
   - Shows loading message while redirecting

3. **`src/hooks/useAuth.ts`**
   - Automatically handles token exchange after Auth0 callback
   - Redirects new users to onboarding
   - No manual intervention needed

4. **`src/pages/Login.tsx`**
   - **DELETED** - No longer needed!

5. **`src/App.tsx`**
   - Removed `/login` route

## Quick Debug Checklist

- [ ] Auth0 dashboard has `http://localhost:5173` in Allowed Callback URLs
- [ ] No typos in callback URL (no trailing slash, no https, etc.)
- [ ] `.env` has correct `VITE_APP_URL` value
- [ ] Restarted frontend dev server after changing `.env`
- [ ] Clicked "Save Changes" in Auth0 dashboard
- [ ] Cleared browser cache/cookies
- [ ] No `VITE_AUTH0_CLIENT_SECRET` in `.env`

## Support

If you're still having issues:
1. Check Auth0 dashboard logs (Monitoring → Logs)
2. Check browser console for errors
3. Check network tab for failed requests
4. Verify Auth0 app settings are saved
