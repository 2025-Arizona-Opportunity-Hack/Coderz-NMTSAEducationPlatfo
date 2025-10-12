# NMTSA LMS Frontend - Quick Start Guide

## 🚀 Getting Started (5 Minutes)

### 1. Install & Build

```bash
cd nmtsa_lms
npm install
npm run build
```

### 2. Add Apps to Django

In `settings.py`, ensure these apps are in `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... existing apps
    'student_dash',
    'teacher_dash',
    'admin_dash',
    'lms',
]
```

### 3. Test the Frontend

Start Django development server:

```bash
python manage.py runserver
```

Visit: `http://localhost:8000/`

---

## 📁 File Structure (What You Got)

```
✅ Base Template + Theme System
   nmtsa_lms/templates/base.html

✅ Public Pages
   nmtsa_lms/templates/landing.html

✅ Authentication Pages
   nmtsa_lms/templates/auth/
   ├── login.html
   ├── signup.html
   └── password_reset.html

✅ Reusable Components
   nmtsa_lms/templates/components/
   ├── navbar.html
   ├── sidebar.html
   ├── button.html
   ├── card.html
   ├── progress_bar.html
   ├── alert.html
   └── form_field.html

✅ Student Dashboard
   student_dash/templates/student_dash/
   ├── dashboard.html
   ├── course_catalog.html
   └── my_courses.html

✅ Teacher Dashboard
   teacher_dash/templates/teacher_dash/
   └── dashboard.html

✅ Admin Dashboard
   admin_dash/templates/admin_dash/
   └── dashboard.html

✅ CSS System
   nmtsa_lms/static/css/
   ├── input.css (source + custom styles)
   └── output.css (compiled - auto-generated)

✅ Configuration
   ├── tailwind.config.js (Tailwind setup)
   ├── package.json (NPM dependencies)
   └── FRONTEND_DOCUMENTATION.md (full docs)
```

---

## 🎨 Design Features

### 4 Autism-Friendly Themes
- 🌞 **Light Calm** - Soft, warm colors (default)
- 🌙 **Dark Calm** - Muted dark for low light
- ⚫ **High Contrast** - Black/white WCAG AAA
- 📄 **Minimal** - No CSS for screen readers

### 4 Font Size Options
- A- Small (14px)
- A Medium (16px - default)
- A+ Large (18px)
- A++ Extra Large (20px)

### 🎯 Key Features
- ✅ Zero animations (autism-friendly)
- ✅ Muted color palette (no sensory overload)
- ✅ Large click targets (48px minimum)
- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ WCAG 2.1 AAA compliant

---

## 🧩 Component Usage Cheat Sheet

### Button
```django
{% include 'components/button.html' with
   text='Save Changes'
   variant='primary'
   size='lg'
   href='/save/'
%}
```
Variants: `primary`, `secondary`, `outline`, `success`, `danger`

### Card
```django
{% include 'components/card.html' with
   title='Course Title'
   content='<p>Description here</p>'
%}
```

### Progress Bar
```django
{% include 'components/progress_bar.html' with
   percentage=75
   label='Course Progress'
%}
```

### Alert
```django
{% include 'components/alert.html' with
   type='success'
   message='Saved successfully!'
   dismissible=True
%}
```
Types: `success`, `info`, `warning`, `error`

### Form Field
```django
{% include 'components/form_field.html' with
   label='Email'
   type='email'
   name='email'
   required=True
%}
```

### Sidebar Navigation
```django
{% include 'components/sidebar.html' with
   active='dashboard'
   items=sidebar_items
%}
```

---

## 🎨 Color Palette

| Purpose | Hex | Use Case |
|---------|-----|----------|
| Primary | `#7FA8C9` | Buttons, links |
| Success | `#A8C9A8` | Success messages |
| Info | `#B8D4E6` | Info messages |
| Warning | `#E6D8B8` | Warnings |
| Error | `#D9A8A8` | Errors |
| Background | `#F5F5F0` | Page background |
| Card | `#FFFFFF` | Card backgrounds |
| Text | `#5A5A52` | Primary text |
| Border | `#D9D9D4` | Borders |

---

## 📝 Template Inheritance

All pages extend `base.html`:

```django
{% extends 'base.html' %}

{% block title %}My Page Title{% endblock %}

{% block content %}
  <!-- Your content here -->
{% endblock %}

{% block extra_css %}
  <!-- Optional extra CSS -->
{% endblock %}

{% block extra_js %}
  <!-- Optional extra JavaScript -->
{% endblock %}
```

---

## 🔧 Common Tasks

### Update CSS After Changes
```bash
npm run build
```

### Watch CSS During Development
```bash
npm run dev
```
(Automatically rebuilds CSS when you save changes)

### Add a New Page
1. Create `myapp/templates/myapp/mypage.html`
2. Extend `base.html`
3. Add your content in `{% block content %}`
4. Create view in `myapp/views.py`
5. Add URL in `myapp/urls.py`

### Change Theme Colors
Edit `tailwind.config.js` → Rebuild CSS

### Add New Component
Create `nmtsa_lms/templates/components/mycomponent.html`

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| CSS not updating | Run `npm run build` and hard refresh (Ctrl+F5) |
| Theme not saving | Check browser localStorage (F12 → Console) |
| Component not showing | Verify template path and context variables |
| Styles not applying | Check `output.css` is loaded in `base.html` |

---

## 📚 Next Steps

1. ✅ **Connect to Backend**
   - Create views for each template
   - Set up URL routing
   - Pass context data to templates

2. ✅ **Add Missing Pages**
   - Course detail page
   - Lesson player (video/blog)
   - Certificate page
   - Profile settings

3. ✅ **Integrate Auth0**
   - Configure OAuth login
   - Test authentication flow

4. ✅ **Test Accessibility**
   - Test with screen readers
   - Validate WCAG compliance
   - Test keyboard navigation

5. ✅ **Deploy**
   - Run `npm run build` for minified CSS
   - Run `python manage.py collectstatic`
   - Configure static file serving

---

## 📖 Full Documentation

For detailed information, see:
- `FRONTEND_DOCUMENTATION.md` - Complete frontend guide
- `PLAN.md` - Original project plan
- Django docs: https://docs.djangoproject.com/

---

## 🎯 Design Principles

**"Clarity is kindness."**

Every design decision prioritizes:
1. Reducing sensory overload
2. Creating predictable patterns
3. Providing user control
4. Supporting diverse needs

---

## 💡 Tips

- Always use components instead of custom HTML
- Test all changes in all 4 themes
- Use spacing variables (var(--spacing-lg))
- No animations (autism-friendly)
- Large click targets (48px minimum)
- Clear, specific language (no idioms)

---

## ✅ Checklist for New Pages

- [ ] Extends `base.html`
- [ ] Uses existing components
- [ ] Tested in all 4 themes
- [ ] Keyboard navigable
- [ ] Clear focus indicators
- [ ] Semantic HTML
- [ ] No animations
- [ ] Mobile responsive
- [ ] WCAG AAA compliant

---

**Happy coding! 🎉**

If you have questions, refer to `FRONTEND_DOCUMENTATION.md` or contact the team.
