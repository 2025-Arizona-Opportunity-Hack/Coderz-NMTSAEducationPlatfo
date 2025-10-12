#!/bin/bash
# Quick start script for i18n localization setup
# Run this after implementing translation markers in your code

echo "🌍 NMTSA LMS - Translation Setup"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from nmtsa_lms/ directory."
    exit 1
fi

echo "📝 Step 1: Generating translation files for all languages..."
echo ""

# Generate for Spanish
echo "  • Generating Spanish (es)..."
python manage.py makemessages -l es --ignore=node_modules --ignore=staticfiles --ignore=.venv

# Generate for French
echo "  • Generating French (fr)..."
python manage.py makemessages -l fr --ignore=node_modules --ignore=staticfiles --ignore=.venv

# Generate for German
echo "  • Generating German (de)..."
python manage.py makemessages -l de --ignore=node_modules --ignore=staticfiles --ignore=.venv

# Generate for Portuguese
echo "  • Generating Portuguese (pt)..."
python manage.py makemessages -l pt --ignore=node_modules --ignore=staticfiles --ignore=.venv

# Generate for Chinese Simplified
echo "  • Generating Chinese Simplified (zh-hans)..."
python manage.py makemessages -l zh_hans --ignore=node_modules --ignore=staticfiles --ignore=.venv

echo ""
echo "✅ Translation files generated!"
echo ""
echo "📁 Files created in:"
echo "   locale/es/LC_MESSAGES/django.po"
echo "   locale/fr/LC_MESSAGES/django.po"
echo "   locale/de/LC_MESSAGES/django.po"
echo "   locale/pt/LC_MESSAGES/django.po"
echo "   locale/zh_hans/LC_MESSAGES/django.po"
echo ""
echo "📋 Next steps:"
echo "   1. Edit the .po files and fill in msgstr values"
echo "   2. Run: python manage.py compilemessages"
echo "   3. Restart the development server"
echo "   4. Test by switching language in Settings dialog"
echo ""
echo "📚 Documentation: docs/LOCALIZATION_GUIDE.md"
