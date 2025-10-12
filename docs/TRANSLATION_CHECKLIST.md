# 📋 HTML Templates Translation Checklist

## Summary
**Total Files:** 60 HTML templates  
**Status:** In Progress  
**Priority Order:** Landing → Auth → Student → Teacher → Admin → Components

---

## ✅ Already Completed
- [x] `base.html` - Added {% load i18n %} and dynamic lang attribute
- [x] `components/settings_dialog.html` - Integrated Django i18n language switcher
- [x] `components/language_switcher.html` - REMOVED (using settings dialog instead)

---

## 🔥 Priority 1: Landing & Public Pages (High Traffic)

### Landing & Marketing
- [ ] `nmtsa_lms/templates/landing.html` - Main homepage
- [ ] `nmtsa_lms/templates/faq.html` - FAQ page
- [ ] `nmtsa_lms/templates/contact.html` - Contact page

### Legal Pages (Required)
- [ ] `nmtsa_lms/templates/legal/privacy.html` - Privacy policy
- [ ] `nmtsa_lms/templates/legal/terms.html` - Terms of service
- [ ] `nmtsa_lms/templates/legal/cookies.html` - Cookie policy

---

## 🔐 Priority 2: Authentication Flow (Critical Path)

### Auth Pages
- [ ] `nmtsa_lms/templates/authentication/select_role.html` - Role selection
- [ ] `nmtsa_lms/templates/authentication/student_onboarding.html` - Student setup
- [ ] `nmtsa_lms/templates/authentication/teacher_onboarding.html` - Teacher setup
- [ ] `nmtsa_lms/templates/authentication/admin_login.html` - Admin login
- [ ] `nmtsa_lms/templates/authentication/profile_settings.html` - Profile settings
- [ ] `nmtsa_lms/templates/auth/login.html` - OAuth login
- [ ] `nmtsa_lms/templates/auth/signup.html` - Sign up
- [ ] `nmtsa_lms/templates/auth/password_reset.html` - Password reset

---

## 🎓 Priority 3: Student Dashboard (Core User Experience)

### Main Student Views
- [ ] `student_dash/templates/student_dash/dashboard.html` - Student dashboard
- [ ] `student_dash/templates/student_dash/my_courses.html` - Enrolled courses
- [ ] `student_dash/templates/student_dash/course_catalog.html` - Browse courses
- [ ] `nmtsa_lms/templates/student_dash/course_catalog.html` - Public catalog
- [ ] `nmtsa_lms/templates/student_dash/course_detail.html` - Course details (public)
- [ ] `nmtsa_lms/templates/student_dash/learning.html` - Lesson viewer
- [ ] `nmtsa_lms/templates/student_dash/certificate.html` - Certificate view

### Student Course Interaction
- [ ] `student_dash/templates/student_dash/course_discussions.html` - Discussions
- [ ] `student_dash/templates/student_dash/discussion_detail.html` - Discussion thread
- [ ] `student_dash/templates/student_dash/discussion_form.html` - Post discussion
- [ ] `student_dash/templates/student_dash/checkout.html` - Payment page

---

## 👨‍🏫 Priority 4: Teacher Dashboard (Content Creators)

### Main Teacher Views
- [ ] `teacher_dash/templates/teacher_dash/dashboard.html` - Teacher dashboard
- [ ] `teacher_dash/templates/teacher_dash/verification_status.html` - Verification pending
- [ ] `teacher_dash/templates/teacher_dash/course_analytics.html` - Course stats

### Course Management
- [ ] `teacher_dash/templates/teacher_dash/course_form.html` - Create/edit course
- [ ] `teacher_dash/templates/teacher_dash/course_detail.html` - Course overview
- [ ] `teacher_dash/templates/teacher_dash/course_preview.html` - Preview course
- [ ] `teacher_dash/templates/teacher_dash/module_form.html` - Create/edit module
- [ ] `teacher_dash/templates/teacher_dash/module_detail.html` - Module overview
- [ ] `teacher_dash/templates/teacher_dash/lesson_form.html` - Create/edit lesson

### Teacher Discussions
- [ ] `teacher_dash/templates/teacher_dash/course_discussions.html` - Manage discussions
- [ ] `teacher_dash/templates/teacher_dash/discussion_detail.html` - Discussion thread
- [ ] `teacher_dash/templates/teacher_dash/discussion_form.html` - Post discussion

---

## 🔧 Priority 5: Admin Dashboard (Platform Management)

### Admin Views
- [ ] `admin_dash/templates/admin_dash/dashboard.html` - Admin dashboard
- [ ] `admin_dash/templates/admin_dash/verify_teachers.html` - Teacher verification list
- [ ] `admin_dash/templates/admin_dash/verify_teacher_detail.html` - Verify teacher
- [ ] `admin_dash/templates/admin_dash/review_courses.html` - Course review list
- [ ] `admin_dash/templates/admin_dash/review_course_detail.html` - Review course

---

## 🧩 Priority 6: Reusable Components (Shared UI)

### Navigation & Layout
- [x] `nmtsa_lms/templates/components/navbar.html` - Main navigation (CHECKED - no lang switcher needed)
- [ ] `nmtsa_lms/templates/components/breadcrumbs.html` - Breadcrumb navigation

### UI Components (May need translation)
- [ ] `nmtsa_lms/templates/components/alert.html` - Alert messages
- [ ] `nmtsa_lms/templates/components/empty_state.html` - Empty state messages
- [ ] `nmtsa_lms/templates/components/confirm_dialog.html` - Confirmation dialogs
- [ ] `nmtsa_lms/templates/components/chat.html` - Chat interface
- [ ] `nmtsa_lms/templates/components/accordion.html` - Accordion widget
- [ ] `nmtsa_lms/templates/components/button.html` - Button component
- [ ] `nmtsa_lms/templates/components/card.html` - Card component
- [ ] `nmtsa_lms/templates/components/form_field.html` - Form field
- [ ] `nmtsa_lms/templates/components/progress_bar.html` - Progress indicator
- [ ] `nmtsa_lms/templates/components/progress_steps.html` - Step indicator
- [ ] `nmtsa_lms/templates/components/spinner.html` - Loading spinner
- [ ] `nmtsa_lms/templates/components/tooltip.html` - Tooltip

### Schema/SEO Components (Minimal translation)
- [ ] `nmtsa_lms/templates/components/breadcrumb_schema.html` - Schema.org markup
- [ ] `nmtsa_lms/templates/components/course_schema.html` - Course schema

---

## 📊 Translation Progress Tracker

### By Category
- **Landing/Public:** 0/6 (0%)
- **Authentication:** 0/8 (0%)
- **Student Dashboard:** 0/11 (0%)
- **Teacher Dashboard:** 0/12 (0%)
- **Admin Dashboard:** 0/5 (0%)
- **Components:** 1/18 (6%)

### Overall Progress
**3/60 templates completed (5%)**

---

## 🎯 Translation Strategy

### What to Translate
1. **Headings & Titles** - All `<h1>`, `<h2>`, `<h3>`, etc.
2. **Button Text** - All button labels and CTAs
3. **Form Labels** - Input labels, placeholders, help text
4. **Navigation** - Menu items, links, breadcrumbs
5. **Messages** - Success, error, info messages
6. **Static Content** - Paragraphs, descriptions, instructions
7. **Alt Text** - Image alternative text for accessibility
8. **ARIA Labels** - Screen reader text

### What NOT to Translate
1. **Email addresses** - Keep as-is
2. **URLs** - Keep as-is (unless creating localized URLs)
3. **Technical IDs** - CSS classes, data attributes
4. **Code/Variables** - `{{ variable_names }}`
5. **Schema.org markup** - Keep English for SEO
6. **API endpoints** - Keep as-is

### Translation Patterns

**Simple text:**
```django
{% load i18n %}
<h1>{% trans "Welcome" %}</h1>
```

**With variables:**
```django
<p>{% blocktrans with name=user.name %}Hello {{ name }}{% endblocktrans %}</p>
```

**Pluralization:**
```django
{% blocktrans count counter=items|length %}
{{ counter }} item
{% plural %}
{{ counter }} items
{% endblocktrans %}
```

**With context:**
```django
<h2>{% trans "Course" context "education" %}</h2>
```

---

## 🚀 Execution Plan

### Phase 1: Foundation (Current)
1. ✅ Configure i18n settings
2. ✅ Add middleware
3. ✅ Set up locale directory
4. ✅ Integrate language switcher in settings dialog
5. 🔄 Translate core templates

### Phase 2: Content Translation
1. Translate all templates (in priority order above)
2. Generate .po files for all languages
3. Add sample translations for testing
4. Compile and test each language

### Phase 3: Python Code
1. Translate model verbose names
2. Translate form labels and errors
3. Translate view messages (success/error)
4. Translate email templates

### Phase 4: JavaScript
1. Identify JS strings needing translation
2. Mark with gettext()
3. Generate djangojs.po files
4. Test JS translations

### Phase 5: Quality Assurance
1. Test all user flows in each language
2. Check for untranslated strings
3. Verify layout doesn't break with longer translations
4. Accessibility testing in all languages

---

## 📝 Notes

- Start with **landing.html** - highest impact
- Each file should add `{% load i18n %}` at the top
- Use `{% trans %}` for simple strings
- Use `{% blocktrans %}` for strings with variables/HTML
- Keep context comments for translators
- Test each template after translation

---

**Last Updated:** October 12, 2025  
**Next Action:** Start with landing.html translation
