#!/usr/bin/env python3
"""
Manual Translation File Creator
================================
Creates basic .po files without requiring GNU gettext tools.
Useful for Windows development when gettext is not available.

Usage:
    python create_manual_translations.py
"""

import os
from pathlib import Path

def create_po_file(language_code, language_name):
    """Create a basic .po file manually"""
    
    locale_dir = Path('locale') / language_code / 'LC_MESSAGES'
    locale_dir.mkdir(parents=True, exist_ok=True)
    
    po_file = locale_dir / 'django.po'
    
    # Basic .po file structure
    content = f'''# NMTSA LMS Translation File
# Language: {language_name} ({language_code})
# 
msgid ""
msgstr ""
"Project-Id-Version: NMTSA LMS 1.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2025-10-12 12:00+0000\\n"
"PO-Revision-Date: 2025-10-12 12:00+0000\\n"
"Last-Translator: NMTSA Team\\n"
"Language-Team: {language_name}\\n"
"Language: {language_code}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"

# Landing Page - Hero Section
msgid "Welcome to NMTSA Learning"
msgstr ""

msgid "Professional education in neurologic music therapy for autism support, healthcare professionals, and families"
msgstr ""

msgid "Get Started for Free"
msgstr ""

msgid "Browse Courses"
msgstr ""

msgid "Go to Dashboard"
msgstr ""

msgid "Teacher Dashboard"
msgstr ""

msgid "Admin Dashboard"
msgstr ""

msgid "Complete Your Profile"
msgstr ""

# Landing Page - Who We Serve
msgid "Who We Serve"
msgstr ""

msgid "Healthcare Professionals"
msgstr ""

msgid "Earn professional credits and certifications in neurologic music therapy techniques for working with individuals with autism and neurologic conditions."
msgstr ""

msgid "Learn More"
msgstr ""

msgid "Families & Caregivers"
msgstr ""

msgid "Educators & Therapists"
msgstr ""

# Common UI Elements
msgid "Login"
msgstr ""

msgid "Logout"
msgstr ""

msgid "Sign Up"
msgstr ""

msgid "Settings"
msgstr ""

msgid "Profile"
msgstr ""

msgid "Dashboard"
msgstr ""

msgid "Courses"
msgstr ""

msgid "My Courses"
msgstr ""

msgid "Home"
msgstr ""

msgid "About"
msgstr ""

msgid "Contact"
msgstr ""

msgid "FAQ"
msgstr ""

msgid "Privacy Policy"
msgstr ""

msgid "Terms of Service"
msgstr ""

# Buttons & Actions
msgid "Submit"
msgstr ""

msgid "Cancel"
msgstr ""

msgid "Save"
msgstr ""

msgid "Delete"
msgstr ""

msgid "Edit"
msgstr ""

msgid "Back"
msgstr ""

msgid "Next"
msgstr ""

msgid "Close"
msgstr ""

msgid "Search"
msgstr ""

msgid "Filter"
msgstr ""

# Messages
msgid "Success!"
msgstr ""

msgid "Error"
msgstr ""

msgid "Warning"
msgstr ""

msgid "Loading..."
msgstr ""

msgid "Please wait"
msgstr ""

# Form Labels
msgid "Email"
msgstr ""

msgid "Password"
msgstr ""

msgid "Name"
msgstr ""

msgid "First Name"
msgstr ""

msgid "Last Name"
msgstr ""

msgid "Phone"
msgstr ""

msgid "Message"
msgstr ""

msgid "Subject"
msgstr ""

# ARIA Labels
msgid "Welcome hero"
msgstr ""

msgid "Go to student dashboard"
msgstr ""

msgid "Browse available courses"
msgstr ""

msgid "Go to teacher dashboard"
msgstr ""

msgid "Go to admin dashboard"
msgstr ""

msgid "Complete your profile setup"
msgstr ""

msgid "Sign up to get started"
msgstr ""

msgid "Learn more about resources for healthcare professionals"
msgstr ""

# Meta Tags
msgid "NMTSA Learning - Professional Neurologic Music Therapy Education"
msgstr ""

msgid "Transform lives through professional neurologic music therapy education. Autism-friendly LMS for healthcare professionals, therapists, and families. Earn certifications online with accessible, sensory-aware design."
msgstr ""

msgid "Professional neurologic music therapy education with autism-friendly design. Earn certifications online for autism support and healthcare."
msgstr ""

msgid "neurologic music therapy, NMT certification, autism therapy, music therapy education, professional development, healthcare education, autism-friendly learning, sensory-accessible platform, online courses"
msgstr ""

# Add more as you find them in your templates...
'''
    
    with open(po_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Created {po_file}")
    return po_file

def add_sample_translations(po_file, language_code):
    """Add sample translations for testing"""
    
    # Sample translations (Spanish only for now)
    translations = {
        'es': {
            "Welcome to NMTSA Learning": "Bienvenido a NMTSA Learning",
            "Get Started for Free": "Comenzar Gratis",
            "Browse Courses": "Explorar Cursos",
            "Learn More": "Saber Más",
            "Who We Serve": "A Quién Servimos",
            "Healthcare Professionals": "Profesionales de la Salud",
            "Login": "Iniciar Sesión",
            "Logout": "Cerrar Sesión",
            "Sign Up": "Registrarse",
            "Settings": "Configuración",
            "Dashboard": "Panel de Control",
            "Courses": "Cursos",
            "My Courses": "Mis Cursos",
            "Submit": "Enviar",
            "Cancel": "Cancelar",
            "Save": "Guardar",
            "Delete": "Eliminar",
            "Edit": "Editar",
            "Search": "Buscar",
            "Loading...": "Cargando...",
            "Email": "Correo Electrónico",
            "Password": "Contraseña",
            "Name": "Nombre",
        }
    }
    
    if language_code not in translations:
        print(f"  No sample translations for {language_code}")
        return
    
    # Read current content
    with open(po_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add translations
    trans_dict = translations[language_code]
    for english, translated in trans_dict.items():
        # Find msgid and add msgstr
        pattern = f'msgid "{english}"\\nmsgstr ""'
        replacement = f'msgid "{english}"\\nmsgstr "{translated}"'
        content = content.replace(pattern, replacement)
    
    # Write back
    with open(po_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Added {len(trans_dict)} sample translations")

def main():
    print("🌍 Creating Translation Files Manually\n")
    
    # Only create Spanish for now
    languages = [
        ('es', 'Spanish'),
        # Uncomment when ready for more languages:
        # ('fr', 'French'),
        # ('de', 'German'),
        # ('pt', 'Portuguese'),
        # ('zh-hans', 'Chinese Simplified'),
    ]
    
    for lang_code, lang_name in languages:
        print(f"Creating {lang_name} ({lang_code})...")
        po_file = create_po_file(lang_code, lang_name)
        
        # Add sample translations for Spanish
        if lang_code == 'es':
            add_sample_translations(po_file, lang_code)
    
    print("\n✅ Translation files created!")
    print("\n📋 Next steps:")
    print("  1. Edit locale/es/LC_MESSAGES/django.po")
    print("  2. Fill in the msgstr values with Spanish translations")
    print("  3. Run: python compile_polib.py")
    print("  4. Restart server and test language switching\n")

if __name__ == '__main__':
    main()
