# 🤖 Option 2: Automated Translation Wrapping

## Terminal Commands for Automated Translation

### Prerequisites
```bash
# Make sure you're in the project root
cd c:/Users/presyze/Projects/ASU/nmstaeducationlms

# Verify Python is available
python --version
```

---

## Step 1: Dry Run (Check What Will Change)

### Check a single file
```bash
python auto_translate.py --check nmtsa_lms/nmtsa_lms/templates/landing.html
```

### Check all priority templates (recommended first)
```bash
python auto_translate.py --check --priority
```
**This checks:**
- landing.html
- faq.html  
- contact.html
- authentication/select_role.html
- authentication/student_onboarding.html
- authentication/teacher_onboarding.html

### Check ALL templates (use with caution)
```bash
python auto_translate.py --check --all
```
**This will scan ~60 template files**

---

## Step 2: Apply Changes

### Process priority templates (RECOMMENDED)
```bash
python auto_translate.py --priority
```
**What it does:**
- ✅ Adds `{% load i18n %}` if missing
- ✅ Wraps headings (h1-h6) with `{% trans %}`
- ✅ Wraps button text with `{% trans %}`
- ✅ Wraps simple link text with `{% trans %}`
- ✅ Wraps `aria-label` attributes
- ✅ Wraps `alt` attributes
- ✅ Wraps `placeholder` attributes
- ✅ Creates `.bak` backup files
- ⚠️ Skips complex content with Django variables

### Process a specific file
```bash
python auto_translate.py nmtsa_lms/nmtsa_lms/templates/faq.html
```

### Process multiple specific files
```bash
python auto_translate.py \
  nmtsa_lms/nmtsa_lms/templates/landing.html \
  nmtsa_lms/nmtsa_lms/templates/faq.html \
  nmtsa_lms/nmtsa_lms/templates/contact.html
```

### Process ALL templates (use after testing priority)
```bash
python auto_translate.py --all
```

---

## Step 3: Review Changes

### Check what changed
```bash
# Use git diff if you're in a git repo
cd nmtsa_lms
git diff nmtsa_lms/templates/landing.html

# Or compare with backup
diff nmtsa_lms/templates/landing.html nmtsa_lms/templates/landing.html.bak
```

### View specific file
```bash
# Open in your editor
code nmtsa_lms/nmtsa_lms/templates/landing.html

# Or view in terminal
cat nmtsa_lms/nmtsa_lms/templates/landing.html | head -50
```

---

## Step 4: Manual Review & Fixes

The script handles **~70-80% of translations automatically**, but you'll need to manually handle:

1. **Paragraph text** - The script skips these to avoid breaking HTML structure
2. **Complex content** - Text with Django variables like `{{ user.name }}`
3. **Multi-line text** - Requires `{% blocktrans %}`
4. **Pluralization** - Requires `{% blocktrans count %}`

### Manual fixes needed (examples):

**Before (automated):**
```django
{% load i18n %}
<h1>{% trans "Welcome" %}</h1>
<p>Professional education for healthcare...</p>  {# ← NOT translated #}
```

**After (manual fix):**
```django
{% load i18n %}
<h1>{% trans "Welcome" %}</h1>
<p>{% trans "Professional education for healthcare..." %}</p>
```

**For content with variables:**
```django
<p>
    {% blocktrans with name=user.name %}
    Hello {{ name }}, welcome back!
    {% endblocktrans %}
</p>
```

---

## Step 5: Generate Translation Files

### Generate for Spanish
```bash
cd nmtsa_lms
python manage.py makemessages -l es --ignore=node_modules --ignore=staticfiles --ignore=.venv
```

### Generate for all configured languages
```bash
python manage.py makemessages --all --ignore=node_modules --ignore=staticfiles --ignore=.venv
```

### Or use the custom command
```bash
python manage.py generate_translations
```

---

## Step 6: Add Sample Translations

### Edit the .po file
```bash
# Open in your editor
code locale/es/LC_MESSAGES/django.po

# Or use nano/vim
nano locale/es/LC_MESSAGES/django.po
```

### Example entries to add:
```po
msgid "Welcome to NMTSA Learning"
msgstr "Bienvenido a NMTSA Learning"

msgid "Get Started for Free"
msgstr "Comenzar Gratis"

msgid "Browse Courses"
msgstr "Explorar Cursos"

msgid "Who We Serve"
msgstr "A Quién Servimos"

msgid "Healthcare Professionals"
msgstr "Profesionales de la Salud"

msgid "Learn More"
msgstr "Saber Más"
```

---

## Step 7: Compile Translations

```bash
cd nmtsa_lms
python manage.py compilemessages
```

**You should see:**
```
processing file django.po in locale/es/LC_MESSAGES
processing file django.po in locale/fr/LC_MESSAGES
...
```

---

## Step 8: Test Language Switching

### Start the development server
```bash
python manage.py runserver
```

### Test in browser
1. Open http://localhost:8000/en/
2. Click Settings (gear icon)
3. Change language to "Spanish"
4. Verify translations appear
5. Test navigation (URLs change to /es/)

### Test different URLs directly
```bash
# English
http://localhost:8000/en/

# Spanish
http://localhost:8000/es/

# French
http://localhost:8000/fr/
```

---

## Step 9: Rollback if Needed

### Restore from backups
```bash
cd nmtsa_lms

# Restore a single file
cp nmtsa_lms/templates/landing.html.bak nmtsa_lms/templates/landing.html

# Restore all backups
find . -name "*.html.bak" | while read backup; do
  original="${backup%.bak}"
  cp "$backup" "$original"
  echo "Restored $original"
done

# Delete backups after verification
find . -name "*.html.bak" -delete
```

### Or use git
```bash
# Discard changes to a file
git checkout nmtsa_lms/templates/landing.html

# Discard all changes
git checkout .
```

---

## Complete Workflow Example

### Full automation for priority templates:
```bash
# 1. Dry run first (check output)
python auto_translate.py --check --priority

# 2. Apply changes if satisfied
python auto_translate.py --priority

# 3. Manual review in editor
code nmtsa_lms/nmtsa_lms/templates/

# 4. Fix any complex cases manually
# (paragraphs, variables, plurals)

# 5. Generate translation files
cd nmtsa_lms
python manage.py makemessages -l es --ignore=node_modules

# 6. Add Spanish translations
code locale/es/LC_MESSAGES/django.po
# Add translations for msgstr values

# 7. Compile
python manage.py compilemessages

# 8. Test
python manage.py runserver
# Visit http://localhost:8000/
# Settings → Language → Spanish

# 9. Verify everything works
# Check layout, broken strings, etc.

# 10. Clean up backups
find nmtsa_lms -name "*.html.bak" -delete
```

---

## Troubleshooting

### Script not found
```bash
# Make sure you're in the right directory
pwd
# Should be: /c/Users/presyze/Projects/ASU/nmstaeducationlms

ls auto_translate.py
# Should exist
```

### Permission denied
```bash
# Make script executable (Linux/Mac)
chmod +x auto_translate.py

# On Windows, just use python
python auto_translate.py --help
```

### UnicodeDecodeError
```bash
# The script handles UTF-8, but if issues persist:
python auto_translate.py --priority 2>&1 | iconv -f UTF-8 -t UTF-8 -c
```

### Too many changes at once
```bash
# Process one file at a time
python auto_translate.py nmtsa_lms/nmtsa_lms/templates/landing.html
# Review
# Then next file
python auto_translate.py nmtsa_lms/nmtsa_lms/templates/faq.html
```

---

## Safety Features

✅ **Backups created automatically** - Every modified file gets a `.bak` copy  
✅ **Dry run mode** - Test with `--check` before applying  
✅ **Skips complex content** - Won't break Django template logic  
✅ **Preserves formatting** - Maintains indentation and structure  
✅ **Idempotent** - Safe to run multiple times  

---

## What Gets Translated Automatically

| Element | Example | Result |
|---------|---------|--------|
| Headings | `<h1>Welcome</h1>` | `<h1>{% trans "Welcome" %}</h1>` |
| Buttons | `<button>Submit</button>` | `<button>{% trans "Submit" %}</button>` |
| Links (simple) | `<a>Learn More</a>` | `<a>{% trans "Learn More" %}</a>` |
| ARIA labels | `aria-label="Close"` | `aria-label="{% trans 'Close' %}"` |
| Alt text | `alt="Logo"` | `alt="{% trans 'Logo' %}"` |
| Placeholders | `placeholder="Search"` | `placeholder="{% trans 'Search' %}"` |

---

## What Needs Manual Translation

| Element | Why Skipped | How to Fix |
|---------|-------------|------------|
| Paragraphs | Could break HTML | Wrap with `{% trans %}` |
| Variables | `{{ user.name }}` | Use `{% blocktrans %}` |
| Multi-line | Complexity | Use `{% blocktrans %}` |
| Mixed content | HTML + text | Split or use `{% blocktrans %}` |
| Dynamic content | Template logic | Context-dependent |

---

## Estimated Time Savings

**Manual translation:** 25-35 hours  
**Automated + manual review:** 10-15 hours  
**Time saved:** ~60%

**Breakdown:**
- Script execution: 2 minutes
- Automated coverage: 70-80%
- Manual fixes: 3-5 hours
- Review & testing: 2-3 hours
- Total: 5-8 hours for priority templates

---

## Next Steps After Automation

1. ✅ Run script on priority templates
2. ✅ Manual review and fixes
3. ✅ Generate .po files
4. ✅ Add sample translations
5. ✅ Test language switching
6. ⏭️ Expand to more templates
7. ⏭️ Hire translators or use AI for full translations
8. ⏭️ Complete remaining 40 templates

---

**Ready to start? Run:**
```bash
python auto_translate.py --check --priority
```

This will show you what changes will be made without modifying any files!
