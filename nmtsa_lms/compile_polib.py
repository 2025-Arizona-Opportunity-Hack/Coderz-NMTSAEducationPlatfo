#!/usr/bin/env python3
"""
Compile .po to .mo files using polib
This properly handles UTF-8 encoding and all gettext features
"""

import polib
from pathlib import Path

def compile_translations():
    """Compile all .po files to .mo files"""
    
    locale_dir = Path('locale')
    
    if not locale_dir.exists():
        print("❌ No locale directory found!")
        return
    
    print("🔨 Compiling translations with polib...\n")
    
    languages_to_compile = ['es']
    compiled = 0
    
    for po_file in locale_dir.rglob('*.po'):
        language = po_file.parent.parent.name
        
        if language not in languages_to_compile:
            print(f"Skipping: {language}")
            continue
        
        print(f"Processing: {po_file.relative_to(locale_dir)}")
        
        try:
            # Load .po file
            po = polib.pofile(str(po_file))
            
            # Show stats
            translated = len([e for e in po if e.translated()])
            print(f"  Found {translated} translations")
            
            # Compile to .mo
            mo_file = po_file.with_suffix('.mo')
            po.save_as_mofile(str(mo_file))
            
            print(f"  ✓ Created {mo_file.name}")
            compiled += 1
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully compiled {compiled} translation file(s)")
    print(f"{'='*60}\n")
    
    print("🎉 Next steps:")
    print("  1. Restart your Django server (Ctrl+C, then: python manage.py runserver)")
    print("  2. Visit http://localhost:8000/")
    print("  3. Click Settings → Change language to Spanish")
    print("  4. Verify translations appear!\n")

if __name__ == '__main__':
    compile_translations()
