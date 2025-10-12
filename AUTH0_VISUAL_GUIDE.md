# Auth0 Dashboard - Visual Configuration Guide

## What You Should See in Auth0

### 1. Application Type Section (Top of Page)

```
┌──────────────────────────────────────────────────────┐
│ Application                                           │
│                                                       │
│ Name: [Your App Name]                                │
│ Type: Single Page Application                   ✅   │
│                                                       │
│ Domain: dev-kdcc586gsnydqn1y.us.auth0.com           │
│ Client ID: CwdXRlCdFbZt0Nk2HsAOnUnRa6r0iFwI         │
└──────────────────────────────────────────────────────┘
```

**If you see "Regular Web Application" or anything else instead:**
❌ You need to create a NEW application as "Single Page Application"

### 2. Application URIs Section (Middle of Page)

```
┌──────────────────────────────────────────────────────┐
│ Application URIs                                      │
│                                                       │
│ Allowed Callback URLs                                │
│ ┌────────────────────────────────────────────────┐  │
│ │ http://localhost:5173/callback                  │  │
│ └────────────────────────────────────────────────┘  │
│                                                       │
│ Allowed Logout URLs                                  │
│ ┌────────────────────────────────────────────────┐  │
│ │ http://localhost:5173                           │  │
│ └────────────────────────────────────────────────┘  │
│                                                       │
│ Allowed Web Origins                                  │
│ ┌────────────────────────────────────────────────┐  │
│ │ http://localhost:5173                           │  │
│ └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### 3. Advanced Settings → Grant Types Tab

```
┌──────────────────────────────────────────────────────┐
│ Advanced Settings                                     │
│                                                       │
│ [OAuth] [Grant Types] [Endpoints] [Certificates]    │
│                                                       │
│ Grant Types:                                          │
│                                                       │
│ ☑ Implicit                                           │
│ ☑ Authorization Code                                 │
│ ☑ Refresh Token                                      │
│ ☐ Device Code                                        │
│ ☐ Password                                           │
│ ☐ Client Credentials                                 │
└──────────────────────────────────────────────────────┘
```

## Copy-Paste URLs

### For Allowed Callback URLs:
```
http://localhost:5173/callback
```

### For Allowed Logout URLs:
```
http://localhost:5173
```

### For Allowed Web Origins:
```
http://localhost:5173
```

## Creating a New Application (If Needed)

If your application type is NOT "Single Page Application":

### Step 1: Create New Application
1. Go to Applications → Applications
2. Click "+ Create Application" button

### Step 2: Configure
```
┌──────────────────────────────────────────────────────┐
│ Create Application                                    │
│                                                       │
│ Name:                                                 │
│ ┌────────────────────────────────────────────────┐  │
│ │ NMTSA Learn Frontend                            │  │
│ └────────────────────────────────────────────────┘  │
│                                                       │
│ Choose an application type:                           │
│                                                       │
│ ○ Native                                             │
│ ○ Single Page Web Applications              ✅       │
│ ○ Regular Web Applications                           │
│ ○ Machine to Machine Applications                    │
│                                                       │
│              [Cancel]  [Create]                      │
└──────────────────────────────────────────────────────┘
```

3. Select "Single Page Web Applications"
4. Click "Create"

### Step 3: Copy New Client ID

After creation, you'll see:
```
┌──────────────────────────────────────────────────────┐
│ Quick Start   Settings   Connections   APIs          │
│                                                       │
│ Domain: dev-kdcc586gsnydqn1y.us.auth0.com           │
│ Client ID: [NEW ID HERE - COPY THIS]                │
│ Client Secret: [Hidden] ⚠️ Don't need this!         │
└──────────────────────────────────────────────────────┘
```

### Step 4: Update .env File

Edit `frontend/.env`:
```env
VITE_AUTH0_CLIENT_ID=[PASTE NEW CLIENT ID HERE]
```

### Step 5: Restart Dev Server
```bash
# Stop current server (Ctrl+C)
# Start again
npm run dev
```

## Verification

### In Browser Console:
After saving Auth0 settings, refresh your app and check console:

```
✅ Should see:
🔐 Auth0 Configuration:
  Domain: dev-kdcc586gsnydqn1y.us.auth0.com
  Client ID: CwdXRlCdFbZt0Nk2HsAOnUnRa6r0iFwI
  Redirect URI: http://localhost:5173/callback
⚠️  Make sure this URL is in Auth0 Dashboard > Application > Allowed Callback URLs
```

### In Auth0 Logs (After Login Attempt):
Go to Monitoring → Logs, you should see:
```
✅ Success Login (s)
   User: [email]
   Connection: google-oauth2
   IP: [your IP]
   Date: [timestamp]
```

NOT:
```
❌ Failed Login (f)
   Error: Callback URL mismatch
   OR
   Error: Unauthorized
```

## Production Setup (Later)

When deploying to production, add your production URLs:

```
Allowed Callback URLs:
http://localhost:5173/callback, https://yourdomain.com/callback

Allowed Logout URLs:
http://localhost:5173, https://yourdomain.com

Allowed Web Origins:
http://localhost:5173, https://yourdomain.com
```

Separate multiple URLs with commas (no spaces).

---

**Remember**: The #1 most common issue is having the wrong Application Type. It MUST be "Single Page Application"!
