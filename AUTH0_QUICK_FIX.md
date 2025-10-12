# Auth0 Integration - Quick Action Guide

## 🚨 IMMEDIATE ACTION REQUIRED

You're getting a **401 Unauthorized** error because your Auth0 application settings need to be configured.

## 📋 5-Minute Fix Checklist

### Step 1: Open Auth0 Dashboard
1. Go to: https://manage.auth0.com/
2. Log in to your account

### Step 2: Find Your Application
1. Click **Applications** → **Applications** in the left sidebar
2. Look for the app with Client ID: `CwdXRlCdFbZt0Nk2HsAOnUnRa6r0iFwI`
3. Click on it to open settings

### Step 3: **CRITICAL** - Check Application Type
Look at the top of the page where it says "Application Type"

**It MUST say:**
```
Single Page Application
```

**If it says anything else** (Regular Web Application, Native, etc.):
- You CANNOT fix this application
- You must create a NEW application:
  1. Go back to Applications list
  2. Click "Create Application"
  3. Name it "NMTSA Learn Frontend"
  4. Choose "Single Page Application"
  5. Copy the new Client ID
  6. Update your `.env` file with the new Client ID

### Step 4: Add Callback URLs

Scroll down to **Application URIs** section.

Copy and paste these EXACT URLs (no extra spaces or characters):

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

⚠️ **IMPORTANT:** 
- Use `http://` NOT `https://`
- No trailing slashes
- Port must be `5173`
- Callback URL must include `/callback` at the end

### Step 5: Enable Grant Types (Advanced Settings)

1. Scroll down and click **Advanced Settings**
2. Click the **Grant Types** tab
3. Make sure these are checked:
   - ✅ Authorization Code
   - ✅ Implicit  
   - ✅ Refresh Token

### Step 6: Save Changes

1. Scroll to the bottom
2. Click **Save Changes** button
3. Wait 30 seconds for changes to take effect

### Step 7: Test Again

1. Close your browser or use incognito mode
2. Go to: http://localhost:5173
3. Click "Login"
4. You should be redirected to Auth0
5. After login, you'll return to your app

## 🎯 Expected Behavior

After configuration:
1. Click Login → Redirects to Auth0
2. See Auth0 login page with social options
3. Choose provider (Google, Microsoft, etc.)
4. Login with that provider
5. Redirect back to `http://localhost:5173/callback`
6. Brief loading screen
7. Redirect to Dashboard
8. **Login button replaced with profile dropdown**

## 🔍 Verify Your Configuration

Open your browser console and you should see:
```
🔐 Auth0 Configuration:
  Domain: dev-kdcc586gsnydqn1y.us.auth0.com
  Client ID: CwdXRlCdFbZt0Nk2HsAOnUnRa6r0iFwI
  Redirect URI: http://localhost:5173/callback
⚠️  Make sure this URL is in Auth0 Dashboard > Application > Allowed Callback URLs
```

This confirms your configuration is correct.

## ❌ Common Mistakes

| Wrong ❌ | Correct ✅ |
|---------|-----------|
| `http://localhost:5173` | `http://localhost:5173/callback` |
| `http://localhost:5173/callback/` | `http://localhost:5173/callback` |
| `https://localhost:5173/callback` | `http://localhost:5173/callback` |
| Application Type: Regular Web App | Application Type: Single Page Application |

## 🆘 Still Not Working?

### Check Auth0 Logs
1. Go to https://manage.auth0.com/
2. Click **Monitoring** → **Logs** in sidebar
3. Look for recent failed login attempts
4. Click on them to see why they failed

### Check Browser Console
1. Press F12 to open DevTools
2. Go to Console tab
3. Look for error messages
4. The error will tell you exactly what's wrong

### Check Network Tab
1. Press F12 to open DevTools
2. Go to Network tab
3. Click Login button
4. Look for the `/oauth/token` request
5. Click on it to see request/response details

## 📞 Need Help?

If you're still stuck after following all steps:
1. Take a screenshot of your Auth0 Application Settings page
2. Take a screenshot of the browser console error
3. Check the detailed troubleshooting guide: `AUTH0_TROUBLESHOOTING.md`

## 🎉 Success Indicators

You'll know it's working when:
- ✅ No 401 errors in console
- ✅ Successfully redirected after login
- ✅ See profile dropdown instead of login button
- ✅ Dashboard page loads
- ✅ Can navigate protected routes

## 📚 Related Files

- **Configuration**: `frontend/src/config/auth0.ts`
- **Callback Page**: `frontend/src/pages/Callback.tsx`
- **Navigation**: `frontend/src/components/layout/Navbar.tsx`
- **Profile Dropdown**: `frontend/src/components/layout/ProfileDropdown.tsx`
- **Environment**: `frontend/.env`

---

**Next Step**: Follow the checklist above, starting with Step 1. The entire process should take less than 5 minutes!
