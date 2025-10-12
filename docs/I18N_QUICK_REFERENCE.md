# 🌍 Django i18n Quick Reference Card

**Languages Supported:** English (en) and Spanish (es)

## 📌 In Templates

```django
{% load i18n %}

{# Simple translation #}
{% trans "Welcome" %}

{# With variables #}
{% blocktrans with name=user.name %}
Hello {{ name }}!
{% endblocktrans %}

{# Pluralization #}
{% blocktrans count counter=items|length %}
{{ counter }} item
{% plural %}
{{ counter }} items
{% endblocktrans %}

{# With context (disambiguation) #}
{% trans "Course" context "education" %}

{# Get current language #}
{% get_current_language as LANGUAGE_CODE %}
{% get_available_languages as LANGUAGES %}
```

## 📌 In Python Code

```python
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy
from django.utils.translation import ngettext, pgettext

# Runtime translation
message = _("Hello World")

# Lazy (for models, forms, class-level)
label = _lazy("Username")

# Pluralization
count = 5
msg = ngettext(
    "%(count)d item",
    "%(count)d items",
    count
) % {'count': count}

# With context
title = pgettext("education", "Course")
```

## 📌 Common Commands

```bash
# Generate translations
python manage.py makemessages -l es
python manage.py makemessages --all

# JavaScript translations
python manage.py makemessages -d djangojs -l es

# Compile translations
python manage.py compilemessages

# Custom command (all at once)
python manage.py generate_translations --compile

# Quick setup
./setup_translations.bat    # Windows
./setup_translations.sh     # Linux/Mac
```

## 📌 File Structure

```
locale/
├── es/LC_MESSAGES/
│   ├── django.po      # Edit this (templates/Python)
│   ├── django.mo      # Generated (don't edit)
│   └── djangojs.po    # JavaScript strings
├── fr/LC_MESSAGES/
└── ...
```

## 📌 .po File Format

```po
# Comment explaining context
msgid "Welcome to our site"
msgstr "Bienvenido a nuestro sitio"

# With variables
msgid "Hello %(name)s"
msgstr "Hola %(name)s"

# Plurals
msgid "%(count)d item"
msgid_plural "%(count)d items"
msgstr[0] "%(count)d artículo"
msgstr[1] "%(count)d artículos"
```

## 📌 User Experience

**Settings Dialog (Gear Icon) → Language Section**
- Dropdown lists all available languages
- Auto-submit on selection
- Page reloads with new language
- Stored in session (persists across pages)

**URL Structure:**
- `/en/courses/` - English
- `/es/courses/` - Spanish
- `/fr/courses/` - French

## 📌 Best Practices

✅ **DO:**
- Use `{% trans %}` for simple strings
- Use `{% blocktrans %}` for strings with variables/HTML
- Use `gettext_lazy` in models and forms
- Keep complete sentences together
- Provide context for ambiguous words

❌ **DON'T:**
- Don't concatenate translated strings
- Don't use `gettext()` in model definitions
- Don't translate URLs or technical terms
- Don't assume word order is the same

## 📌 Workflow

```
1. Mark strings       → {% trans "text" %}
2. Generate .po       → makemessages
3. Translate          → Edit msgstr in .po files
4. Compile            → compilemessages
5. Restart server     → Changes take effect
6. Test               → Settings → Language
```

## 📌 Troubleshooting

**Not showing?**
```bash
python manage.py compilemessages
# Restart server
```

**Not switching?**
- Check `LocaleMiddleware` in settings
- Check URLs in `i18n_patterns()`
- Clear browser cache

**Strings missing?**
```bash
python manage.py makemessages -l es --no-obsolete
```

## 📌 Quick Tests

```python
# In Django shell
from django.utils.translation import activate, gettext as _

activate('es')
print(_("Welcome"))  # Should print Spanish if translated

activate('en')
print(_("Welcome"))  # Should print English
```

---

**Docs:** `docs/LOCALIZATION_GUIDE.md`  
**Implementation:** `docs/LOCALIZATION_IMPLEMENTATION.md`
