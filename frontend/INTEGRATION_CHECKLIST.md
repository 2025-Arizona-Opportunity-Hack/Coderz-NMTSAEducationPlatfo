# Integration Verification Checklist

Use this checklist to verify that the frontend-backend integration is working correctly.

## Prerequisites

- [ ] Backend Django server is running on `http://localhost:8000`
- [ ] Frontend Vite dev server is running on `http://localhost:5173`
- [ ] `.env` file is configured with correct `VITE_API_BASE_URL`
- [ ] Django CORS is configured to allow `localhost:5173`

## Phase 1: API Layer Testing

### 1. API Configuration

- [ ] Open browser DevTools → Network tab
- [ ] Navigate to any page
- [ ] Verify requests go to `http://localhost:8000/api/v1/`
- [ ] Check that `Authorization: Bearer <token>` header is present on authenticated requests
- [ ] Check that `X-CSRFToken` header is present on POST/PUT/DELETE requests

### 2. Authentication Flow

#### Register New User
- [ ] Navigate to `/register`
- [ ] Fill out registration form
- [ ] Submit form
- [ ] Verify API call to `/api/v1/auth/register/`
- [ ] Verify token is stored in localStorage
- [ ] Verify redirect to dashboard

#### Login Existing User
- [ ] Navigate to `/login`
- [ ] Enter credentials
- [ ] Submit form
- [ ] Verify API call to `/api/v1/auth/login/`
- [ ] Verify token storage
- [ ] Verify redirect based on role:
  - Student → `/dashboard`
  - Instructor → `/teacher/dashboard` (will show 404 until implemented)
  - Admin → `/admin/dashboard` (will show 404 until implemented)

#### Token Refresh
- [ ] Wait for token to expire (or manually remove from localStorage)
- [ ] Make an authenticated request
- [ ] Verify automatic token refresh attempt
- [ ] Verify new token is stored
- [ ] Verify original request is retried with new token

#### Logout
- [ ] Click logout button
- [ ] Verify API call to `/api/v1/auth/logout/`
- [ ] Verify token removed from localStorage
- [ ] Verify redirect to home page

### 3. Protected Routes

#### Unauthenticated Access
- [ ] Clear all tokens from localStorage
- [ ] Try to access `/dashboard`
- [ ] Verify redirect to `/login`
- [ ] Verify return URL is preserved in location state

#### Role-Based Access
- [ ] Login as student
- [ ] Try to access `/teacher/dashboard` (will 404 until implemented)
- [ ] Verify redirect to `/dashboard`
- [ ] Login as instructor
- [ ] Try to access `/admin/dashboard` (will 404 until implemented)
- [ ] Verify redirect to `/teacher/dashboard` (will 404 until implemented)

### 4. Service Layer

Open browser console and test services manually:

```javascript
// Import services in browser console
import { teacherService } from '/src/services/teacher.service.ts';
import { adminService } from '/src/services/admin.service.ts';

// Test teacher service (as instructor)
await teacherService.getDashboardStats();
// Should return: { totalCourses, totalStudents, totalRevenue, averageRating }

await teacherService.getMyCourses();
// Should return: { count, next, previous, results: [] }

// Test admin service (as admin)
await adminService.getDashboardStats();
// Should return: { totalUsers, totalCourses, pendingApplications, ... }

await adminService.getUsers({ page: 1, role: 'student' });
// Should return paginated user list
```

### 5. Type Safety

In VS Code:

- [ ] Open `src/services/teacher.service.ts`
- [ ] Hover over any method
- [ ] Verify JSDoc documentation appears
- [ ] Verify parameter types are shown
- [ ] Verify return type is shown

- [ ] Try calling a service method incorrectly
- [ ] Verify TypeScript error appears
- [ ] Example: `teacherService.createCourse({ title: 'Test' })` (missing required fields)

### 6. Error Handling

#### Django Validation Error
- [ ] Try to create a course with invalid data
- [ ] Verify error response is properly formatted
- [ ] Verify error message is user-friendly
- [ ] Verify field-specific errors are shown

#### Network Error
- [ ] Stop Django backend
- [ ] Try to make an API request
- [ ] Verify "Network error" message appears
- [ ] Restart Django backend
- [ ] Verify requests work again

#### 401 Unauthorized
- [ ] Manually expire or delete auth token
- [ ] Make an authenticated request
- [ ] Verify automatic token refresh attempt
- [ ] If refresh fails, verify redirect to login

### 7. Internationalization

- [ ] Open `src/i18n/locales/en.json`
- [ ] Verify `teacher` section exists
- [ ] Verify `admin` section exists
- [ ] In a component, try accessing a translation:
  ```tsx
  const { t } = useTranslation();
  console.log(t('teacher.dashboard.title')); // "Teacher Dashboard"
  console.log(t('admin.nav.users')); // "User Management"
  ```

## Phase 2: Teacher Dashboard (To Be Implemented)

This section will be completed after teacher pages are implemented.

### Teacher Dashboard
- [ ] Login as instructor
- [ ] Navigate to `/teacher/dashboard`
- [ ] Verify dashboard loads
- [ ] Verify stats are displayed correctly
- [ ] Verify course list is shown

### Create Course
- [ ] Click "Create Course" button
- [ ] Fill out course form
- [ ] Submit form
- [ ] Verify API call to `/api/v1/teacher/courses/create/`
- [ ] Verify course appears in course list

### Manage Modules/Lessons
- [ ] Open a course
- [ ] Add a module
- [ ] Add lessons to module
- [ ] Reorder lessons
- [ ] Upload video
- [ ] Verify progress indicator during upload

### Publish Course
- [ ] Mark course as complete
- [ ] Click "Publish" button
- [ ] Verify API call to `/api/v1/teacher/courses/{id}/publish/`
- [ ] Verify course status changes to "Published"

## Phase 3: Admin Dashboard (To Be Implemented)

This section will be completed after admin pages are implemented.

### Admin Dashboard
- [ ] Login as admin
- [ ] Navigate to `/admin/dashboard`
- [ ] Verify dashboard loads
- [ ] Verify system stats are displayed

### User Management
- [ ] Navigate to `/admin/users`
- [ ] Search for a user
- [ ] Filter by role
- [ ] Edit user details
- [ ] Suspend a user
- [ ] Reactivate a user

### Teacher Applications
- [ ] Navigate to `/admin/applications`
- [ ] View pending applications
- [ ] Open application details
- [ ] Approve an application
- [ ] Reject an application with feedback

### Course Review
- [ ] Navigate to `/admin/courses`
- [ ] View courses pending review
- [ ] Preview a course
- [ ] Approve a course
- [ ] Request changes to a course

## Accessibility Testing

### Keyboard Navigation
- [ ] Use only keyboard (no mouse)
- [ ] Tab through all interactive elements
- [ ] Verify focus indicator is visible
- [ ] Verify no keyboard traps
- [ ] Verify skip link works

### Screen Reader
Using NVDA (Windows) or VoiceOver (Mac):
- [ ] Navigate through site with screen reader
- [ ] Verify page titles are announced
- [ ] Verify form labels are read
- [ ] Verify error messages are announced
- [ ] Verify loading states are announced
- [ ] Verify button purposes are clear

### Color Contrast
- [ ] Use browser DevTools color picker
- [ ] Check contrast ratios of text
- [ ] Verify all text meets 4.5:1 minimum
- [ ] Or use axe DevTools browser extension

### Zoom/Text Resize
- [ ] Zoom to 200% (Ctrl/Cmd + "+")
- [ ] Verify layout doesn't break
- [ ] Verify all content is readable
- [ ] Verify no horizontal scrolling

### Focus Management
- [ ] Open a modal
- [ ] Verify focus moves to modal
- [ ] Close modal
- [ ] Verify focus returns to trigger element

## Performance Testing

### Bundle Size
```bash
npm run build
```
- [ ] Check `dist/` folder size
- [ ] Verify total size is reasonable (<5MB)
- [ ] Check that code splitting is working (multiple JS chunks)

### API Response Time
- [ ] Check Network tab in DevTools
- [ ] Verify API responses are <500ms (with local backend)
- [ ] Check for unnecessary duplicate requests
- [ ] Verify pagination is working (not fetching all data)

### Memory Leaks
- [ ] Navigate between pages multiple times
- [ ] Open DevTools → Memory tab
- [ ] Take heap snapshot
- [ ] Verify memory is released after navigation

## Browser Compatibility

Test in:
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if on Mac)
- [ ] Mobile browsers (Chrome Mobile, Safari iOS)

## Common Issues & Solutions

### Issue: CORS Error
**Symptom**: `Access to XMLHttpRequest at 'http://localhost:8000' from origin 'http://localhost:5173' has been blocked by CORS policy`

**Solution**: Add to Django `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
CORS_ALLOW_CREDENTIALS = True
```

### Issue: 401 Errors
**Symptom**: All authenticated requests return 401

**Solution**: Check that:
1. Token is being stored: `localStorage.getItem('auth-token')`
2. Token is being sent: Check Network tab for `Authorization` header
3. Token is valid: Decode JWT at jwt.io

### Issue: Types Not Working
**Symptom**: TypeScript errors or no autocomplete

**Solution**:
1. Restart VS Code TypeScript server: Cmd/Ctrl+Shift+P → "TypeScript: Restart TS Server"
2. Check `tsconfig.json` includes all `src` files
3. Run `npm install` to ensure dependencies are installed

### Issue: Translations Not Showing
**Symptom**: Translation keys shown instead of text (e.g., "teacher.dashboard.title")

**Solution**:
1. Check `src/i18n/locales/en.json` has the key
2. Check i18n is initialized in `main.tsx`
3. Verify `useTranslation()` hook is used correctly

## Success Criteria

✅ Phase 1 is successful when:
- [ ] All authentication flows work
- [ ] Protected routes enforce authentication
- [ ] Role-based access control works
- [ ] Service methods can be called successfully
- [ ] Error handling works correctly
- [ ] Types provide autocomplete and errors
- [ ] Translations load correctly
- [ ] Accessibility tests pass
- [ ] No console errors
- [ ] Backend logs show successful requests

## Next Steps

After verifying Phase 1:

1. **Start Phase 2**: Implement teacher dashboard pages
   - Follow patterns from `INTEGRATION_GUIDE.md`
   - Use services from `src/services/teacher.service.ts`
   - Use types from `src/types/teacher.ts`
   - Use translations from `src/i18n/locales/en.json`

2. **Write Tests**: Add unit and integration tests
   - Test service methods
   - Test components
   - Test authentication flows

3. **Deploy**: Configure for production
   - Update `.env` with production URLs
   - Build and test production bundle
   - Deploy to hosting service

## Getting Help

If you encounter issues:

1. Check `INTEGRATION_GUIDE.md` for troubleshooting
2. Check browser console for errors
3. Check Django logs for backend errors
4. Check Network tab for failed requests
5. Refer to API docs at `http://localhost:8000/api/docs/`

---

**Last Updated**: October 11, 2025  
**Version**: 1.0.0
