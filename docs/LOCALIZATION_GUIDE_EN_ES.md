# 🌍 NMTSA LMS - Localization Guide (English + Spanish)

## 📋 Overview

The NMTSA LMS supports **bilingual content** with English and Spanish translations using Django's built-in internationalization (i18n) system.

### Supported Languages
- 🇺🇸 **English (en)** - Default language
- 🇪🇸 **Spanish (es)** - Español

---

## 🔧 Technical Setup

### Configuration Files

**Settings** (`nmtsa_lms/settings.py`):
```python
USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = 'en'  # Default

LANGUAGES = [
    ('en', 'English'),
    ('es', 'Spanish (Español)'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # ← Language detection
    # ... other middleware
]
```

**URLs** (`nmtsa_lms/urls.py`):
```python
from django.conf.urls.i18n import i18n_patterns

# Non-translatable URLs (admin, SEO, APIs)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),  # Language switcher
]

# Translatable URLs (automatically get /en/ or /es/ prefix)
urlpatterns += i18n_patterns(
    path('', views.index, name='landing'),
    path('', include('authentication.urls')),
    path('student/', include('student_dash.urls')),
    path('teacher/', include('teacher_dash.urls')),
    path('admin-dash/', include('admin_dash.urls')),
    path('lms/', include('lms.urls')),
    prefix_default_language=True,
)
```

---

## 📂 File Structure

```
nmtsa_lms/
├── locale/
│   └── es/                    # Spanish translations
│       └── LC_MESSAGES/
│           ├── django.po      # Editable translation source
│           └── django.mo      # Compiled binary (auto-generated)
├── compile_polib.py           # Compilation script
├── create_manual_translations.py  # Template generator
└── nmtsa_lms/
    └── templates/
        ├── base.html          # Has {% load i18n %}
        └── components/
            └── settings_dialog.html  # Language switcher UI
```

---

## 🔄 Translation Workflow

### Step 1: Mark Strings for Translation

**In Templates:**
```django
{% load i18n %}

{# Simple strings #}
<h1>{% trans "Welcome to NMTSA" %}</h1>

{# Strings with variables #}
{% blocktrans with name=user.name %}
Hello {{ name }}!
{% endblocktrans %}

{# Pluralization #}
{% blocktrans count total=course_count %}
{{ total }} course available
{% plural %}
{{ total }} courses available
{% endblocktrans %}
```

**In Python Code:**
```python
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

# For runtime strings
message = _("User successfully enrolled")

# For model fields, form labels (lazy evaluation)
class Course(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name=_lazy("Course Title")
    )
```

### Step 2: Extract Translatable Strings

**Option A: Django's makemessages (requires GNU gettext - not available on Windows)**
```bash
python manage.py makemessages -l es
```

**Option B: Manual Creation (Windows-friendly)**
```bash
python create_manual_translations.py
```
This creates `locale/es/LC_MESSAGES/django.po` with a basic structure.

### Step 3: Add Spanish Translations

Edit `locale/es/LC_MESSAGES/django.po`:
```po
# Example entries
msgid "Welcome to NMTSA Learning"
msgstr "Bienvenido a NMTSA Learning"

msgid "Get Started for Free"
msgstr "Comenzar Gratis"

msgid "Browse Courses"
msgstr "Explorar Cursos"
```

**File Format Rules:**
- `msgid` = English source text (EXACT match from templates)
- `msgstr` = Spanish translation
- Empty `msgstr ""` = not translated (will show English)
- Multi-line strings use continuation format:
```po
msgid ""
"This is a very long "
"string that spans multiple lines"
msgstr ""
"Esta es una cadena muy larga "
"que abarca varias líneas"
```

### Step 4: Compile Translations

**Using polib (recommended - pure Python):**
```bash
python compile_polib.py
```

This converts `.po` (human-readable) → `.mo` (binary format Django uses).

**Output:**
```
🔨 Compiling translations with polib...
Processing: es\LC_MESSAGES\django.po
  Found 43 translations
  ✓ Created django.mo
✅ Successfully compiled 1 translation file(s)
```

### Step 5: Test Translations

1. **Restart Django server:**
```bash
python manage.py runserver
```

2. **Visit:** http://localhost:8000/en/

3. **Change language:**
   - Click Settings (⚙️ gear icon in navbar)
   - Select "Spanish (Español)" from Language dropdown
   - Page automatically reloads with Spanish translations

4. **URL changes:**
   - English: `http://localhost:8000/en/`
   - Spanish: `http://localhost:8000/es/`

---

## 🎨 User Experience

### Language Switcher

Located in **Settings Dialog** (accessible from navbar gear icon):
- Dropdown populated dynamically from `settings.LANGUAGES`
- Auto-submits form on selection
- Page reloads with new language
- Language choice stored in session

### URL Structure

- **Default:** `/en/` (English)
- **Spanish:** `/es/`
- **Admin/APIs:** No prefix (e.g., `/admin/`, `/sitemap.xml`)

Language prefix is automatically added to all user-facing URLs.

---

## 📝 Translation Progress

### ✅ Completed
- Core infrastructure (settings, middleware, URLs)
- Settings dialog integration
- Landing page hero section (~40%)
- Common UI elements (buttons, navigation)

### 🔄 In Progress
- Landing page remaining sections:
  - Families card
  - Educators card
  - Features section
  - How It Works
  - Testimonials
  - Final CTA

### 📋 Pending
- FAQ page (`faq.html`)
- Contact page (`contact.html`)
- Authentication flow (4 templates)
- Student dashboard (11 templates)
- Teacher dashboard (12 templates)
- Admin dashboard (5 templates)

**Total:** ~60 templates requiring translation

---

## 🔍 Debugging Tips

### Translations Not Showing?

1. **Check .mo file exists:**
```bash
ls -la locale/es/LC_MESSAGES/django.mo
```

2. **Recompile translations:**
```bash
python compile_polib.py
```

3. **Restart Django server:**
```bash
# Ctrl+C to stop, then:
python manage.py runserver
```

4. **Verify language in session:**
   - Open browser DevTools → Application → Cookies
   - Check `django_language` cookie = `es`

5. **Check template syntax:**
```django
{% load i18n %}  <!-- Must be at top of template -->
{% trans "exact text from .po file" %}
```

### Common Issues

**Issue:** English shows instead of Spanish
- **Cause:** `msgid` in `.po` doesn't match template text exactly
- **Fix:** Copy exact string from template to `.po` file

**Issue:** UnicodeDecodeError when switching language
- **Cause:** `.mo` file has encoding issues
- **Fix:** Use `compile_polib.py` instead of manual compiler

**Issue:** 404 error after changing language
- **Cause:** URL doesn't exist in new language
- **Fix:** Ensure all URLs wrapped in `i18n_patterns()`

---

## 🛠️ Development Commands

```bash
# Start development server
python manage.py runserver

# Compile translations (after editing .po files)
python compile_polib.py

# Create fresh .po file structure
python create_manual_translations.py

# View translation file
cat locale/es/LC_MESSAGES/django.po

# Check .mo file was created
ls -la locale/es/LC_MESSAGES/
```

---

## 📚 Resources

- **Django i18n docs:** https://docs.djangoproject.com/en/5.2/topics/i18n/
- **Quick reference:** `docs/I18N_QUICK_REFERENCE.md`
- **Implementation details:** `docs/LOCALIZATION_IMPLEMENTATION.md`
- **polib documentation:** https://polib.readthedocs.io/

---

## 🎯 Next Steps

1. **Complete landing page translation** (highest priority - most traffic)
2. **Translate authentication flow** (critical user journey)
3. **Add FAQ/Contact translations** (high value for users)
4. **Student dashboard** (core user experience)
5. **Teacher dashboard** (creator experience)
6. **Consider professional translation service** for accuracy

---

**Note:** Only English and Spanish are currently supported. Additional languages can be added by:
1. Adding to `LANGUAGES` in `settings.py`
2. Creating `locale/{lang_code}/LC_MESSAGES/` directory
3. Following translation workflow above
