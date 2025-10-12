# Schema.org Implementation Guide

## Overview
We've implemented comprehensive Schema.org structured data for SEO enhancement. This enables rich snippets in Google search results, better indexing, and improved visibility.

---

## 1. Course Schema (Course Detail Pages)

### Usage in Course Detail Templates

Add this to any course detail page (student or teacher view):

```django
{% extends 'base.html' %}

{% block extra_schema %}
    {% include 'components/course_schema.html' with course=course %}
{% endblock %}

{% block content %}
    <!-- Your course content here -->
{% endblock %}
```

### What It Provides
- **Course Name & Description**
- **Provider** (NMTSA Learning)
- **Instructor Information**
- **Pricing** (free or paid with amount)
- **Educational Level** (Beginner/Intermediate/Advanced)
- **Duration** (courseWorkload)
- **Keywords/Tags**
- **Course Image**
- **Publication Dates**
- **Certificate Information**

### Example Output in Google Search
```
NMTSA Learning
Introduction to Neurologic Music Therapy ★★★★★
$49.99 • 5 hours • Certificate included
Learn evidence-based music therapy techniques for autism support...
```

---

## 2. Breadcrumb Schema (All Pages)

### Automatic Implementation
Breadcrumbs are **automatically generated** for all pages via context processor.

**No template changes needed!** The breadcrumb schema is injected into `base.html` automatically.

### How It Works
```python
# nmtsa_lms/context_processors.py
def breadcrumbs(request):
    # Analyzes current URL path
    # Returns breadcrumb list
    # Example: [{'name': 'Home', 'url': '/'}, {'name': 'Courses', 'url': '/student/catalog/'}]
```

### Path-Specific Breadcrumbs

#### Student Pages
- `/` → Home
- `/student/catalog/` → Home > Courses
- `/student/course/123/` → Home > Courses > Course Details

#### Teacher Pages
- `/teacher/dashboard/` → Home > Teacher > Dashboard
- `/teacher/courses/` → Home > Teacher > Courses
- `/teacher/courses/create/` → Home > Teacher > Courses > Create Course

#### Admin Pages
- `/admin-dash/` → Home > Admin
- `/admin-dash/verify-teachers/` → Home > Admin > Verify Teachers

### Visual Breadcrumbs Component

If you want to display visual breadcrumbs (recommended for UX):

```django
{% if breadcrumbs and breadcrumbs|length > 1 %}
    {% include 'components/breadcrumbs.html' with items=breadcrumbs %}
{% endif %}
```

This shows:
```
Home > Courses > Introduction to NMT
```

With:
- Clickable links (except current page)
- ARIA labels for accessibility
- Keyboard navigation support
- Theme-aware styling

---

## 3. Organization Schema (Site-Wide)

**Already implemented in `base.html`**

Provides:
- Organization name (NMTSA Learning)
- Description
- Logo
- Social media profiles (Facebook, LinkedIn)
- Contact information
- Type: EducationalOrganization

---

## 4. Additional Schema Types (Future)

### VideoObject Schema
For video lessons:

```json
{
  "@type": "VideoObject",
  "name": "Lesson Title",
  "description": "Lesson description",
  "thumbnailUrl": "...",
  "uploadDate": "2025-01-01",
  "duration": "PT10M",
  "contentUrl": "...",
  "embedUrl": "..."
}
```

### FAQ Schema
For FAQ pages:

```json
{
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "What is NMT?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "..."
    }
  }]
}
```

### Review/Rating Schema
For course reviews:

```json
{
  "@type": "AggregateRating",
  "ratingValue": "4.8",
  "reviewCount": "127",
  "bestRating": "5",
  "worstRating": "1"
}
```

---

## Implementation Checklist

### ✅ Completed
- [x] Organization schema (site-wide)
- [x] Breadcrumb schema (auto-generated)
- [x] Course schema template component
- [x] Context processor for breadcrumbs
- [x] Visual breadcrumb component

### ⏳ Pending (Manual Implementation)
- [ ] Add `{% block extra_schema %}` to all course detail templates
- [ ] Add visual breadcrumbs to page headers
- [ ] Test course schema with Google Rich Results Test
- [ ] Verify breadcrumbs appear in search results

### 🔮 Future Enhancements
- [ ] VideoObject schema for lessons
- [ ] Review/Rating schema for courses
- [ ] FAQ schema for help pages
- [ ] Event schema for live courses/webinars
- [ ] Person schema for instructor profiles

---

## Testing Your Schema

### 1. Google Rich Results Test
https://search.google.com/test/rich-results

Paste your page URL or HTML to see:
- Valid schema detected
- Eligible rich result types
- Warnings or errors

### 2. Schema Markup Validator
https://validator.schema.org/

Validates JSON-LD structured data.

### 3. View Source
Right-click page → View Page Source
Look for `<script type="application/ld+json">` blocks

---

## Example: Updating Course Detail Page

### Before (No Schema)
```django
{% extends 'base.html' %}

{% block content %}
    <h1>{{ course.title }}</h1>
    <p>{{ course.description }}</p>
{% endblock %}
```

### After (With Schema)
```django
{% extends 'base.html' %}

{% block extra_schema %}
    {% include 'components/course_schema.html' with course=course %}
{% endblock %}

{% block content %}
    <!-- Visual breadcrumbs for UX -->
    {% if breadcrumbs and breadcrumbs|length > 1 %}
        {% include 'components/breadcrumbs.html' with items=breadcrumbs %}
    {% endif %}
    
    <h1>{{ course.title }}</h1>
    <p>{{ course.description }}</p>
{% endblock %}
```

**Result**: Course appears in Google search with:
- Star ratings (if reviews exist)
- Price display
- Duration
- Provider badge
- Breadcrumb trail

---

## Troubleshooting

### Schema Not Appearing
1. Clear Django cache: `python manage.py clear_cache`
2. Hard refresh browser: Ctrl+Shift+R
3. Check page source for `<script type="application/ld+json">`
4. Verify context processor is registered in settings.py

### Validation Errors
Common issues:
- **Missing required fields**: Ensure course has title, description
- **Invalid date format**: Use `|date:'c'` filter for ISO 8601
- **JSON syntax errors**: Check for trailing commas, quotes

### Breadcrumbs Not Auto-Generating
1. Check `nmtsa_lms.context_processors.breadcrumbs` in TEMPLATES > context_processors
2. Verify request.path matches expected patterns
3. Add custom logic in `context_processors.py` for new URL patterns

---

## Performance Notes

### Impact
- **Minimal**: JSON-LD is inline, ~2-5KB per page
- **No render blocking**: Loads with HTML
- **Cache-friendly**: Static per page, not per user

### Best Practices
- Use `{% block extra_schema %}` for page-specific schemas
- Keep structured data up-to-date with page content
- Don't duplicate information (breadcrumbs auto-include current page)

---

## Support

For questions or issues:
- Check Django logs: `python manage.py runserver`
- Test with Rich Results Test
- Review Schema.org docs: https://schema.org/Course

---

**Last Updated**: October 11, 2025  
**Version**: 1.0  
**Status**: ✅ Ready for Production
