# Auth0 Dashboard Configuration Checklist

## Current Error
```
POST https://dev-kdcc586gsnydqn1y.us.auth0.com/oauth/token 401 (Unauthorized)
```

This means Auth0 is rejecting the token exchange request.

## Step-by-Step Fix

### 1. Go to Auth0 Dashboard
Visit: https://manage.auth0.com/

### 2. Select Your Application
- Click on **Applications** → **Applications** (in left sidebar)
- Find and click on the application with Client ID: `CwdXRlCdFbZt0Nk2HsAOnUnRa6r0iFwI`

### 3. Verify Application Type
Scroll to the top of the application settings page.

**CRITICAL**: The "Application Type" must be:
```
✅ Single Page Application
```

If it shows anything else (Regular Web Application, Native, Machine to Machine), you need to:
- Delete this application
- Create a new one
- Choose "Single Page Application" during creation
- Update your `.env` file with the new Client ID

### 4. Configure Application URIs
Scroll down to **Application URIs** section.

#### Allowed Callback URLs
Add this EXACT URL (copy and paste):
```
http://localhost:5173/callback
```

#### Allowed Logout URLs
Add this EXACT URL:
```
http://localhost:5173
```

#### Allowed Web Origins
Add this EXACT URL:
```
http://localhost:5173
```

### 5. Grant Types
Scroll to **Advanced Settings** → **Grant Types**

Make sure these are checked:
- ✅ Implicit
- ✅ Authorization Code
- ✅ Refresh Token

### 6. Save Changes
- Click **Save Changes** button at the bottom
- Wait 30-60 seconds for changes to propagate

### 7. Clear Browser Data
Before testing again:
1. Open DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

Or use an incognito/private window

### 8. Test Authentication
1. Clear the URL (remove `?code=...` parameters)
2. Go to: http://localhost:5173
3. Click the Login button
4. You should be redirected to Auth0
5. After login, you should be redirected back to http://localhost:5173/callback
6. Then automatically to http://localhost:5173/dashboard

## Common Issues

### Issue 1: Application Type is Wrong
**Symptom**: 401 error during token exchange
**Fix**: Must be "Single Page Application" - if not, create a new application

### Issue 2: Callback URL Mismatch
**Symptom**: "Callback URL mismatch" error
**Fix**: Use exact URL `http://localhost:5173/callback` (no trailing slash, include /callback)

### Issue 3: Grant Types Not Enabled
**Symptom**: Various authorization errors
**Fix**: Enable Authorization Code, Implicit, and Refresh Token in Advanced Settings

### Issue 4: Social Connections Not Enabled
**Symptom**: Can't see Google/Microsoft/etc login options
**Fix**: Go to Authentication → Social → Enable desired providers

## Verification Checklist

After configuration, verify:
- [ ] Application Type = "Single Page Application"
- [ ] Allowed Callback URLs contains: `http://localhost:5173/callback`
- [ ] Allowed Logout URLs contains: `http://localhost:5173`
- [ ] Allowed Web Origins contains: `http://localhost:5173`
- [ ] Grant Types include: Authorization Code, Implicit, Refresh Token
- [ ] Social connections are enabled (if you want to use them)
- [ ] Changes have been saved (click Save Changes button)

## Screenshot Guide

Here's what you should see in Auth0:

**Application Type** (at top of page):
```
Single Page Application
```

**Application URIs** section should look like:
```
Allowed Callback URLs:
http://localhost:5173/callback

Allowed Logout URLs:
http://localhost:5173

Allowed Web Origins:
http://localhost:5173
```

## Still Not Working?

If you still get 401 errors after following all steps:

1. **Double-check Application Type**
   - It MUST be "Single Page Application"
   - If it's not, you cannot change it - you must create a new application

2. **Check Auth0 Logs**
   - Go to Monitoring → Logs in Auth0 dashboard
   - Look for failed login attempts
   - The error message will tell you what's wrong

3. **Verify in Network Tab**
   - Open DevTools → Network tab
   - Click Login
   - Look for the `/oauth/token` request
   - Check the request payload and response

4. **Try Without Social Connections**
   - Create a test user in Auth0 (Database connection)
   - Try logging in with username/password
   - This helps isolate if the issue is with social connections

## Need More Help?

Check Auth0 logs at: https://manage.auth0.com/dashboard/us/{your-tenant}/logs

The logs will show exactly why the authentication is failing.
