# OAuth Setup Guide - URGENT

## 🚨 Current Issue: "Missing required parameter: client_id"

You're seeing this error because the OAuth client IDs are not configured in your `.env` file.

## ✅ Quick Fix (5 minutes)

### Step 1: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Go to **"APIs & Services" → "Credentials"**
4. Click **"Create Credentials" → "OAuth 2.0 Client ID"**
5. If prompted, configure OAuth consent screen first:
   - User Type: **External**
   - App name: **NMTSA Learn**
   - User support email: Your email
   - Developer contact: Your email
   - Save and continue through remaining steps
6. Back in Credentials, create OAuth 2.0 Client ID:
   - Application type: **Web application**
   - Name: **NMTSA Learn Frontend**
   - Authorized JavaScript origins:
     - `http://localhost:5173`
     - `http://localhost:5174` (optional, for multiple instances)
   - Click **Create**
7. **Copy the Client ID** (looks like: `123456789-abcdefgh.apps.googleusercontent.com`)

### Step 2: Update Your .env File

Open `frontend/.env` and replace the placeholder with your actual Client ID:

```bash
# Before:
VITE_GOOGLE_CLIENT_ID=your-google-client-id-here.apps.googleusercontent.com

# After (use YOUR actual Client ID):
VITE_GOOGLE_CLIENT_ID=123456789-abcdefgh.apps.googleusercontent.com
```

### Step 3: Restart Dev Server

```bash
# Stop the current dev server (Ctrl+C)
# Start it again
pnpm run dev
```

### Step 4: Test

1. Go to `http://localhost:5173/login`
2. Click "Sign in with Google"
3. Should now open Google OAuth popup without errors

---

## 🔧 What Was Fixed

### ✅ Removed Register Page
- Deleted `frontend/src/pages/Register.tsx`
- Removed register route from `App.tsx`
- Updated Login page text to remove "create account" link

### ✅ Added Onboarding Flow
- Created `/onboarding` route (protected)
- New users automatically redirected after OAuth login
- Existing users go straight to dashboard
- Two-step onboarding:
  1. Role selection (Student vs Teacher)
  2. Profile completion (role-specific forms)

### ✅ Updated Login Flow
```
User clicks "Sign in with Google"
  ↓
Google OAuth authenticates
  ↓
Frontend receives user data
  ↓
Backend checks if user exists
  ↓
Returns: { token, user, isNewUser: true/false }
  ↓
isNewUser = true → /onboarding
isNewUser = false → /dashboard
```

---

## 📋 Optional: Microsoft OAuth Setup

If you also want Microsoft login:

1. Go to [Azure Portal](https://portal.azure.com/)
2. **Azure Active Directory** → **App registrations** → **New registration**
3. Name: **NMTSA Learn**
4. Supported account types: **Accounts in any organizational directory and personal Microsoft accounts**
5. Redirect URI:
   - Platform: **Single-page application (SPA)**
   - URL: `http://localhost:5173`
6. Click **Register**
7. Copy the **Application (client) ID**
8. Add to `.env`:

```bash
VITE_MICROSOFT_CLIENT_ID=your-microsoft-app-id-here
VITE_MICROSOFT_AUTHORITY=https://login.microsoftonline.com/common
VITE_MICROSOFT_REDIRECT_URI=http://localhost:5173
```

---

## 🎯 Current Routes

| Route | Description | Protected |
|-------|-------------|-----------|
| `/login` | OAuth login (Google + Microsoft) | No |
| `/onboarding` | New user onboarding | Yes |
| `/dashboard` | Student dashboard | Yes |
| `/admin/login` | Admin username/password login | No |

**Note:** `/register` has been removed - all registration now happens through OAuth

---

## 🐛 Troubleshooting

### "redirect_uri_mismatch"
- **Problem:** Redirect URI not configured in Google Console
- **Fix:** Add `http://localhost:5173` to authorized JavaScript origins

### "Access blocked: This app's request is invalid"
- **Problem:** OAuth consent screen not configured
- **Fix:** Complete OAuth consent screen setup in Google Console

### "Popup closed by user"
- **Problem:** User manually closed popup
- **Fix:** This is normal behavior, no action needed

### OAuth popup doesn't open
- **Problem:** Popup blocker
- **Fix:** Allow popups for localhost:5173

### Still seeing "Missing required parameter: client_id"
- **Problem:** Environment variable not loaded or dev server not restarted
- **Fix:** 
  1. Verify `.env` file has correct `VITE_GOOGLE_CLIENT_ID`
  2. Stop dev server completely (Ctrl+C)
  3. Restart: `pnpm run dev`
  4. Hard refresh browser (Ctrl+Shift+R)

---

## 📚 Next Steps After OAuth is Working

1. **Test the full onboarding flow:**
   - Login with Google (new user)
   - Should redirect to `/onboarding`
   - Select Student or Teacher role
   - Complete profile form
   - Should redirect to dashboard

2. **Test existing user flow:**
   - Login with same Google account again
   - Should go directly to `/dashboard`

3. **Backend migrations:**
   ```bash
   cd backend/nmtsa_lms
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Verify backend API endpoints work:**
   - `/api/auth/oauth/signin` - OAuth login
   - `/api/onboarding/select-role` - Role selection
   - `/api/onboarding/teacher` - Teacher onboarding
   - `/api/onboarding/student` - Student onboarding

---

## 🚀 Production Deployment

When deploying to production:

1. **Create production OAuth credentials:**
   - Add your production domain to authorized origins
   - Example: `https://nmtsa-learn.com`

2. **Update production .env:**
   ```bash
   VITE_GOOGLE_CLIENT_ID=your-production-client-id
   VITE_APP_URL=https://nmtsa-learn.com
   ```

3. **Backend OAuth endpoint:**
   - Already simplified - no token validation needed
   - Just receives user data from frontend
   - Creates/finds user and returns JWT

---

## 💡 Key Changes Summary

| What Changed | Before | After |
|--------------|--------|-------|
| Registration | Separate `/register` page | OAuth only, new users → onboarding |
| Login flow | OAuth → Dashboard | OAuth → Check if new → Onboarding or Dashboard |
| Register route | Existed | **Removed** |
| Onboarding | Not implemented | **Full 2-step flow added** |
| OAuth handling | Backend validates tokens | **Frontend only, backend receives user data** |

---

Need help? Check:
- `backend/OAUTH_IMPLEMENTATION.md` - Detailed OAuth docs
- `backend/SETUP_CHECKLIST.md` - Full setup guide
- `frontend/.env.example` - Environment variable template
