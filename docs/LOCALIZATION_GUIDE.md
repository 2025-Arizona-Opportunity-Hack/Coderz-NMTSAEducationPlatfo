# 🌍 Multi-Language Localization Guide for NMTSA LMS

## Overview
The NMTSA LMS now supports **multi-language localization** using Django's built-in i18n (internationalization) system. This allows the platform to serve users in multiple languages without managing JSON files manually.

## 🎯 Currently Supported Languages
- **English** (en) - Default
- **Spanish** (es)
- **French** (fr)
- **German** (de)
- **Portuguese** (pt)
- **Chinese Simplified** (zh-hans)

## 🚀 Quick Start

### For Developers: Adding Translations

#### 1. Mark Translatable Strings in Templates

**Simple text translation:**
```django
{% load i18n %}

<h1>{% trans "Welcome to NMTSA Learning" %}</h1>
<p>{% trans "Start your neurologic music therapy journey today" %}</p>
```

**Translation with variables (blocktrans):**
```django
{% load i18n %}

<p>
    {% blocktrans with username=user.username %}
    Hello {{ username }}, welcome back!
    {% endblocktrans %}
</p>

<p>
    {% blocktrans count counter=course_count %}
    You have {{ counter }} course.
    {% plural %}
    You have {{ counter }} courses.
    {% endblocktrans %}
</p>
```

**Translation with context (disambiguation):**
```django
{% load i18n %}

{# "Course" as in educational course #}
<h2>{% trans "Course" context "education" %}</h2>

{# "Course" as in direction/path #}
<p>{% trans "Course" context "navigation" %}</p>
```

#### 2. Mark Translatable Strings in Python Code

**In views.py:**
```python
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy
from django.utils.translation import ngettext

def my_view(request):
    # Runtime translation
    message = _("Course created successfully!")
    
    # Lazy translation (for strings evaluated later)
    form_label = _lazy("Enter your name")
    
    # Plural translation
    count = 5
    message = ngettext(
        "%(count)d course available",
        "%(count)d courses available",
        count
    ) % {'count': count}
    
    return render(request, 'template.html', {'message': message})
```

**In models.py (use lazy translation):**
```python
from django.utils.translation import gettext_lazy as _

class Course(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name=_("Course Title"),
        help_text=_("Enter the title of the course")
    )
    
    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
```

**In forms.py:**
```python
from django.utils.translation import gettext_lazy as _

class CourseForm(forms.Form):
    title = forms.CharField(
        label=_("Title"),
        help_text=_("Enter course title"),
        error_messages={
            'required': _("This field is required."),
            'max_length': _("Title is too long.")
        }
    )
```

#### 3. Generate Translation Files

After marking strings, generate `.po` files for each language:

```bash
cd nmtsa_lms

# Generate for specific language
python manage.py makemessages -l es  # Spanish
python manage.py makemessages -l fr  # French
python manage.py makemessages -l de  # German
python manage.py makemessages -l pt  # Portuguese
python manage.py makemessages -l zh_hans  # Chinese Simplified

# Or generate for all configured languages at once
python manage.py makemessages --all

# Include JavaScript files (if using JS translations)
python manage.py makemessages -d djangojs -l es
```

This creates/updates files in:
```
nmtsa_lms/locale/
├── es/
│   └── LC_MESSAGES/
│       ├── django.po      # Template/Python translations
│       └── djangojs.po    # JavaScript translations
├── fr/
│   └── LC_MESSAGES/
│       └── django.po
└── ...
```

#### 4. Edit Translation Files

Open the `.po` files and add translations:

**Example: `locale/es/LC_MESSAGES/django.po`**
```po
#: nmtsa_lms/templates/landing.html:15
msgid "Welcome to NMTSA Learning"
msgstr "Bienvenido a NMTSA Learning"

#: teacher_dash/views.py:42
msgid "Course created successfully!"
msgstr "¡Curso creado exitosamente!"

#: teacher_dash/models.py:25
msgid "Course Title"
msgstr "Título del Curso"
```

**Tips for editing `.po` files:**
- `msgid` is the original English string (DON'T change)
- `msgstr` is the translation (FILL THIS IN)
- Comments starting with `#:` show where the string is used
- Use `#, fuzzy` flag for uncertain translations

#### 5. Compile Translations

After editing `.po` files, compile them to binary `.mo` files:

```bash
python manage.py compilemessages
```

This creates `.mo` files that Django uses at runtime. **You must compile after every change to `.po` files.**

#### 6. Test Translations

**Option 1: URL Prefix**
Visit:
- `http://localhost:8000/en/` - English
- `http://localhost:8000/es/` - Spanish
- `http://localhost:8000/fr/` - French

**Option 2: Language Switcher**
Use the language dropdown in the navbar (globe icon).

**Option 3: Browser Language**
Set your browser's preferred language and Django will auto-detect it.

## 🛠️ Advanced Usage

### JavaScript Translations

For translating strings in JavaScript:

**1. Include the JavaScript catalog in your template:**
```django
<script src="{% url 'javascript-catalog' %}"></script>
```

**2. Use `gettext()` in JavaScript:**
```javascript
// Simple translation
const message = gettext("Welcome!");
alert(message);

// Interpolation
const text = interpolate(
    gettext("You have %s messages"),
    [5]
);

// Plural forms
const count = 3;
const text = ngettext(
    "One course",
    "%(count)s courses",
    count
);
```

**3. Mark JS strings for translation:**
```javascript
// In your .js file
const messages = {
    success: gettext("Success!"),
    error: gettext("An error occurred"),
    confirm: gettext("Are you sure?")
};
```

**4. Generate JS translations:**
```bash
python manage.py makemessages -d djangojs -l es
```

### Translation Best Practices

#### ✅ DO:
- Use `{% trans %}` for simple strings without variables
- Use `{% blocktrans %}` for strings with variables or HTML
- Use `gettext_lazy` (`_lazy`) in models, forms, and class-level code
- Keep strings complete and meaningful (avoid concatenation)
- Provide context when a word has multiple meanings
- Use comments to explain context to translators

```python
# Good: Complete sentence with context
_("Welcome to the course dashboard")

# Good: Clear variable names
_("Hello %(username)s, you have %(count)d new messages") % {
    'username': user.username,
    'count': message_count
}
```

#### ❌ DON'T:
- Don't concatenate translated strings
- Don't use `gettext()` in models (use `gettext_lazy()`)
- Don't translate URLs or technical identifiers
- Don't assume word order is the same across languages

```python
# Bad: String concatenation
_("Hello") + " " + user.username  # Word order varies!

# Good: Single string with variable
_("Hello %(username)s") % {'username': user.username}
```

### Handling Pluralization

Different languages have different plural rules. Use `ngettext` or `blocktrans count`:

**Python:**
```python
from django.utils.translation import ngettext

count = len(courses)
message = ngettext(
    "%(count)d course",
    "%(count)d courses",
    count
) % {'count': count}
```

**Template:**
```django
{% blocktrans count counter=courses|length %}
{{ counter }} course available
{% plural %}
{{ counter }} courses available
{% endblocktrans %}
```

### Translation Context for Disambiguation

When the same word has different meanings:

**Python:**
```python
from django.utils.translation import pgettext

# "Course" in educational context
course_title = pgettext("education", "Course")

# "Course" as in direction/path
navigation_text = pgettext("navigation", "Course")
```

**Template:**
```django
{% trans "Course" context "education" %}
{% trans "Course" context "navigation" %}
```

## 🔧 Configuration Reference

### Settings (`settings.py`)

```python
# Enable i18n
USE_I18N = True
USE_L10N = True

# Default language
LANGUAGE_CODE = 'en'

# Supported languages
LANGUAGES = [
    ('en', 'English'),
    ('es', 'Spanish'),
    ('fr', 'French'),
    ('de', 'German'),
    ('pt', 'Portuguese'),
    ('zh-hans', 'Chinese (Simplified)'),
]

# Translation files location
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
```

### Middleware (in `MIDDLEWARE` list):

```python
'django.middleware.locale.LocaleMiddleware',  # Must be after SessionMiddleware
```

### URLs (`urls.py`)

```python
from django.conf.urls.i18n import i18n_patterns

# Translatable URLs with language prefix
urlpatterns += i18n_patterns(
    path('', views.index, name='landing'),
    path('courses/', views.courses, name='courses'),
    # ... other URLs
    prefix_default_language=True,  # Include /en/ for English
)

# Non-translatable URLs (no language prefix)
urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),  # Language switcher
    path('jsi18n/', JavaScriptCatalog.as_view()),     # JS translations
]
```

## 📝 Common Commands Cheat Sheet

```bash
# Generate translation files
python manage.py makemessages -l es              # For Spanish
python manage.py makemessages -l fr              # For French
python manage.py makemessages --all              # For all languages
python manage.py makemessages -d djangojs -l es  # JavaScript only

# Update existing translation files (merge new strings)
python manage.py makemessages -l es --no-obsolete

# Compile translations (required after editing .po files)
python manage.py compilemessages

# Compile for specific language
python manage.py compilemessages -l es

# Check for untranslated strings
msgfmt --check locale/es/LC_MESSAGES/django.po
```

## 🌐 Language Switcher Component

The language switcher is automatically included in the navbar. Users can:
1. Click the globe icon + dropdown (desktop)
2. Use the language selector in the mobile menu
3. Switch languages via URL: `/en/`, `/es/`, `/fr/`, etc.

The selected language is stored in the user's session.

## 🎨 Autism-Friendly Considerations

The localization system maintains NMTSA's autism-friendly design:
- **No animations** during language switching
- **Clear focus states** on language dropdown
- **High contrast mode** support maintained
- **Screen reader friendly** with ARIA labels
- **Keyboard navigation** fully supported
- **Predictable behavior** (no auto-reload, form submission)

## 📚 Resources

- [Django i18n Documentation](https://docs.djangoproject.com/en/stable/topics/i18n/)
- [Translation Best Practices](https://docs.djangoproject.com/en/stable/topics/i18n/translation/)
- [GNU gettext Manual](https://www.gnu.org/software/gettext/manual/)

## 🐛 Troubleshooting

### Translations Not Showing Up

1. **Did you compile?**
   ```bash
   python manage.py compilemessages
   ```

2. **Check `.po` file format:**
   - Make sure `msgstr` is not empty
   - No syntax errors (missing quotes, etc.)

3. **Restart development server:**
   ```bash
   # Ctrl+C to stop, then:
   python manage.py runserver
   ```

4. **Clear browser cache** or use incognito mode

### Language Not Switching

1. **Check middleware order** in `settings.py`:
   - `LocaleMiddleware` must be after `SessionMiddleware`

2. **Check URL patterns**:
   - Are your URLs wrapped in `i18n_patterns()`?

3. **Check browser settings**:
   - Browser language might override selection

### Missing Strings in `.po` Files

1. **Re-run makemessages:**
   ```bash
   python manage.py makemessages -l es --no-obsolete
   ```

2. **Check if strings are marked correctly:**
   - Templates: `{% load i18n %}` at the top
   - Templates: `{% trans "text" %}` or `{% blocktrans %}`
   - Python: `from django.utils.translation import gettext as _`

## 📞 Support

For translation questions or issues:
1. Check this documentation
2. Review Django i18n docs
3. Check `.po` file syntax
4. Verify compilation succeeded
5. Test with simple string first

---

**Last Updated:** October 2025  
**Django Version:** 5.2.7  
**Project:** NMTSA LMS
