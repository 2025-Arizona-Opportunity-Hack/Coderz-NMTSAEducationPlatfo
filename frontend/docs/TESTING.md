# NMTSA Learn - Testing & QA Checklist

## ✅ Functional Testing

### Authentication

- [ ] User can register with valid email and password
- [ ] User receives validation errors for invalid inputs
- [ ] User can log in with correct credentials
- [ ] User receives error message for incorrect credentials
- [ ] User can reset password via forgot password flow
- [ ] User stays logged in after page refresh (persistent auth)
- [ ] User is redirected to login when accessing protected routes while logged out
- [ ] User can log out successfully
- [ ] Auth token is properly stored and removed

### Course Exploration

- [ ] Courses load and display correctly on Explore page
- [ ] Search functionality filters courses by keyword
- [ ] Category filter works correctly
- [ ] Difficulty level filter works correctly
- [ ] Rating filter works correctly
- [ ] Sort by (popularity, rating, newest) functions properly
- [ ] Pagination works and shows correct page numbers
- [ ] Course cards display all required information
- [ ] Clicking a course card navigates to course detail page

### Course Detail Page

- [ ] Course details load correctly
- [ ] Course hero section displays all information
- [ ] Instructor card shows instructor details
- [ ] Course modules/lessons are listed correctly
- [ ] Course reviews display with ratings
- [ ] User can enroll in a course (if authenticated)
- [ ] Enrollment button is disabled for already enrolled courses
- [ ] Tab navigation works (Overview, Curriculum, Reviews)
- [ ] Schema.org structured data is present

### Lesson Viewer

- [ ] Lesson content loads correctly
- [ ] Video player displays and plays video
- [ ] Video controls work (play, pause, seek, volume)
- [ ] Playback speed control functions
- [ ] Skip forward/backward (±10s) buttons work
- [ ] Fullscreen mode works
- [ ] Video captions display if available
- [ ] Progress tracking updates correctly
- [ ] Markdown content renders properly with syntax highlighting
- [ ] Notes sidebar displays existing notes
- [ ] User can add new notes with timestamps
- [ ] Resources list displays all resources
- [ ] Resource download links work
- [ ] Lesson navigation (prev/next) works correctly
- [ ] Completing lesson updates progress

### Dashboard

- [ ] Dashboard stats display correctly
- [ ] Enrolled courses show with accurate progress
- [ ] Continue learning section shows recent courses
- [ ] Course filtering works (all, in-progress, completed)
- [ ] Course search functions properly
- [ ] Pagination works on enrolled courses
- [ ] Certificates display correctly
- [ ] Certificate download works
- [ ] Tab navigation functions (Overview, My Courses, Certificates)

### Applications

- [ ] Applications list displays correctly
- [ ] Status filter tabs work (all, pending, under review, approved, rejected)
- [ ] User can create new application
- [ ] Application form validation works
- [ ] Document upload functions properly
- [ ] Prerequisites checkbox is required
- [ ] Application submission succeeds
- [ ] Application details modal displays all information
- [ ] User can cancel pending applications
- [ ] Pagination works

### Forum

- [ ] Forum posts display correctly
- [ ] Search functionality works
- [ ] Tag filtering functions properly
- [ ] Sort by recent/popular works
- [ ] User can create new post
- [ ] Post creation form validates inputs
- [ ] Tags can be added/removed
- [ ] Popular tags are clickable
- [ ] Post card shows author, timestamp, likes, comments count
- [ ] Clicking post card navigates to post detail
- [ ] Pagination works

## 🎨 UI/UX Testing

### Responsive Design

- [ ] Mobile (< 768px) - All pages render correctly
- [ ] Tablet (768px - 1024px) - Layout adapts properly
- [ ] Desktop (> 1024px) - Full layout displays correctly
- [ ] Navigation menu collapses on mobile
- [ ] Mobile menu opens/closes properly
- [ ] Touch interactions work on mobile devices
- [ ] No horizontal scrolling on any screen size

### Visual Design

- [ ] Color scheme is consistent across all pages
- [ ] Typography is clear and readable
- [ ] Buttons have proper hover/focus states
- [ ] Form inputs have proper focus states
- [ ] Loading spinners display during async operations
- [ ] Error messages are clearly visible
- [ ] Success messages display appropriately
- [ ] Empty states are informative and helpful
- [ ] Images load correctly or show placeholder
- [ ] Icons display correctly

### Navigation

- [ ] Navbar displays correctly on all pages
- [ ] Active navigation link is highlighted
- [ ] All navigation links work correctly
- [ ] Footer displays on all pages
- [ ] Footer links work correctly
- [ ] Skip to content link works
- [ ] Browser back/forward buttons work correctly
- [ ] Breadcrumbs display where applicable

## ♿ Accessibility Testing

### Keyboard Navigation

- [ ] All interactive elements are keyboard accessible
- [ ] Tab order is logical
- [ ] Focus indicators are visible
- [ ] Enter/Space activates buttons and links
- [ ] Escape closes modals and dropdowns
- [ ] Arrow keys navigate in lists/menus
- [ ] No keyboard traps

### Screen Reader

- [ ] Page titles are descriptive
- [ ] Headings are properly hierarchical (h1, h2, h3)
- [ ] Images have alt text
- [ ] Links have descriptive text
- [ ] Buttons have clear labels
- [ ] Form inputs have labels
- [ ] Error messages are announced
- [ ] ARIA labels are used appropriately
- [ ] Dynamic content updates are announced

### Visual Accessibility

- [ ] Color contrast ratios meet WCAG AA standards
- [ ] Text is readable at 200% zoom
- [ ] Focus indicators are visible
- [ ] No information conveyed by color alone
- [ ] Font sizes are appropriate
- [ ] Line height and spacing are adequate

## 🌍 Internationalization Testing

### Language Switching

- [ ] Language switcher displays current language
- [ ] Clicking language switcher changes language
- [ ] All UI text changes to selected language
- [ ] Language preference persists across sessions
- [ ] Date/time formats adapt to language
- [ ] Number formats adapt to language

### Translation Coverage

- [ ] All pages have complete translations
- [ ] Error messages are translated
- [ ] Form validation messages are translated
- [ ] Button labels are translated
- [ ] Navigation items are translated
- [ ] No hardcoded English text remains

## 🔐 Security Testing

### Authentication

- [ ] Passwords are not visible in network requests
- [ ] JWT tokens are stored securely
- [ ] Protected routes require authentication
- [ ] Expired tokens trigger re-authentication
- [ ] XSS protection in user inputs
- [ ] CSRF protection implemented

### Data Validation

- [ ] Client-side validation prevents invalid submissions
- [ ] Server-side validation errors display correctly
- [ ] File uploads validate file types
- [ ] File uploads validate file sizes
- [ ] SQL injection attempts fail
- [ ] Script injection attempts fail

## ⚡ Performance Testing

### Page Load

- [ ] Initial page load < 3 seconds
- [ ] Subsequent page loads < 1 second
- [ ] Images are optimized
- [ ] Code splitting is effective
- [ ] Lazy loading works correctly
- [ ] Bundle size is reasonable

### Runtime Performance

- [ ] No memory leaks detected
- [ ] Smooth scrolling
- [ ] Animations are smooth (60fps)
- [ ] No janky interactions
- [ ] Search is responsive
- [ ] Pagination is fast

## 🔄 State Management Testing

### Zustand Store

- [ ] Auth state persists correctly
- [ ] Profile data updates correctly
- [ ] State rehydration works after refresh
- [ ] Logout clears state properly
- [ ] Multiple tabs sync state correctly

## 📱 Browser Compatibility

### Desktop Browsers

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

### Mobile Browsers

- [ ] Chrome Mobile
- [ ] Safari iOS
- [ ] Firefox Mobile
- [ ] Samsung Internet

## 🐛 Error Handling

### Network Errors

- [ ] Offline state displays error message
- [ ] Failed API calls show error message
- [ ] Retry functionality works
- [ ] Timeout errors display correctly
- [ ] 404 errors display correctly
- [ ] 500 errors display correctly

### User Errors

- [ ] Form validation errors are clear
- [ ] Invalid input triggers proper messages
- [ ] File upload errors are descriptive
- [ ] Permission errors are informative

## 📊 SEO Testing

### Meta Tags

- [ ] All pages have unique titles
- [ ] All pages have meta descriptions
- [ ] Open Graph tags present
- [ ] Twitter Card tags present
- [ ] Canonical URLs set correctly

### Structured Data

- [ ] Course pages have Schema.org data
- [ ] Structured data validates in Google tool
- [ ] Breadcrumbs are properly marked up

## 🔗 Integration Testing

### API Integration

- [ ] All API endpoints are called correctly
- [ ] Request headers are set properly
- [ ] Response data is parsed correctly
- [ ] Error responses are handled
- [ ] Loading states display during requests
- [ ] Concurrent requests handled properly

## ✨ Edge Cases

- [ ] Very long course titles display correctly
- [ ] Empty states display when no data
- [ ] Large datasets (100+ items) perform well
- [ ] Special characters in inputs handled correctly
- [ ] Unicode characters display correctly
- [ ] Very long user names truncate properly
- [ ] Missing images show placeholders
- [ ] Broken API endpoints fail gracefully

## 📝 Notes

### Testing Environment

- Node.js version: 18+
- Browser versions: Latest stable
- Screen sizes tested: 320px, 768px, 1024px, 1920px
- Network conditions: Fast 3G, 4G, WiFi

### Known Issues

- Document any known issues here during testing

### Test Results Summary

- Total tests: **\_**
- Passed: **\_**
- Failed: **\_**
- Blocked: **\_**
- Pass rate: **\_**%

---

**Last Updated**: [Date]
**Tested By**: [Name]
**Version**: 1.0.0
