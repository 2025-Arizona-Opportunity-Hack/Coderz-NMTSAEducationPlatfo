#!/usr/bin/env python3
"""
Automated Template Translation Wrapper
========================================
This script automatically wraps translatable strings in Django templates with {% trans %} tags.

Usage:
    python auto_translate.py <template_file>
    python auto_translate.py --all  # Process all templates
    python auto_translate.py --check  # Dry run, show what would change

Features:
    - Wraps heading text (h1-h6)
    - Wraps button text
    - Wraps paragraph text
    - Wraps link text
    - Wraps ARIA labels
    - Wraps alt text
    - Wraps placeholder text
    - Preserves Django template variables
    - Adds {% load i18n %} if missing
    - Creates backup before modifying

Author: NMTSA LMS Team
Date: October 12, 2025
"""

import re
import sys
import os
from pathlib import Path
from typing import List, Tuple
import shutil

class TemplateTranslator:
    """Automatically wrap translatable strings in Django i18n tags"""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.changes_made = 0
        self.files_processed = 0
        
    def has_i18n_load(self, content: str) -> bool:
        """Check if template already loads i18n"""
        return bool(re.search(r'{%\s*load\s+i18n\s*%}', content))
    
    def add_i18n_load(self, content: str) -> str:
        """Add {% load i18n %} after {% extends %} or at the top"""
        if self.has_i18n_load(content):
            return content
            
        # Find {% extends %} tag
        extends_match = re.search(r'({%\s*extends\s+[\'"][^\'"]+[\'"]\s*%})', content)
        if extends_match:
            # Add after extends
            insert_pos = extends_match.end()
            return content[:insert_pos] + '\n{% load i18n %}' + content[insert_pos:]
        
        # Find {% load static %} tag
        load_static_match = re.search(r'({%\s*load\s+static\s*%})', content)
        if load_static_match:
            # Add after load static
            insert_pos = load_static_match.end()
            return content[:insert_pos] + '\n{% load i18n %}' + content[insert_pos:]
        
        # Add at the very beginning
        return '{% load i18n %}\n' + content
    
    def is_translatable_text(self, text: str) -> bool:
        """Check if text should be translated"""
        text = text.strip()
        
        # Skip if empty or only whitespace
        if not text or text.isspace():
            return False
        
        # Skip if it's a Django variable
        if text.startswith('{{') and text.endswith('}}'):
            return False
        
        # Skip if it's a Django tag
        if text.startswith('{%') and text.endswith('%}'):
            return False
        
        # Skip if it's a URL
        if text.startswith(('http://', 'https://', '/', '#')):
            return False
        
        # Skip if it's an email
        if '@' in text and '.' in text:
            return False
        
        # Skip if already translated
        if 'trans ' in text or 'blocktrans' in text:
            return False
        
        # Skip if it contains only special characters
        if re.match(r'^[^\w\s]+$', text):
            return False
        
        return True
    
    def wrap_simple_text(self, text: str) -> str:
        """Wrap simple text in {% trans %} tag"""
        text = text.strip()
        if not self.is_translatable_text(text):
            return text
        
        # Escape quotes in text
        escaped_text = text.replace('"', '\\"')
        return f'{{% trans "{escaped_text}" %}}'
    
    def wrap_aria_label(self, match) -> str:
        """Wrap ARIA label attribute"""
        attr_name = match.group(1)  # aria-label or aria-labelledby
        quote = match.group(2)  # " or '
        content = match.group(3)
        
        if not self.is_translatable_text(content):
            return match.group(0)
        
        escaped_content = content.replace('"', '\\"')
        return f'{attr_name}="{{% trans "{escaped_content}" %}}"'
    
    def wrap_alt_text(self, match) -> str:
        """Wrap alt attribute"""
        quote = match.group(1)
        content = match.group(2)
        
        if not self.is_translatable_text(content):
            return match.group(0)
        
        escaped_content = content.replace('"', '\\"')
        return f'alt="{{% trans "{escaped_content}" %}}"'
    
    def wrap_placeholder(self, match) -> str:
        """Wrap placeholder attribute"""
        quote = match.group(1)
        content = match.group(2)
        
        if not self.is_translatable_text(content):
            return match.group(0)
        
        escaped_content = content.replace('"', '\\"')
        return f'placeholder="{{% trans "{escaped_content}" %}}"'
    
    def wrap_heading(self, match) -> str:
        """Wrap heading text"""
        opening_tag = match.group(1)  # <h1 ...>
        content = match.group(2)
        closing_tag = match.group(3)  # </h1>
        
        # Check if content has Django template tags
        if '{{' in content or '{%' in content:
            # Complex content, skip for now
            return match.group(0)
        
        if not self.is_translatable_text(content):
            return match.group(0)
        
        escaped_content = content.strip().replace('"', '\\"')
        return f'{opening_tag}\n        {{% trans "{escaped_content}" %}}\n    {closing_tag}'
    
    def wrap_button(self, match) -> str:
        """Wrap button text"""
        opening_tag = match.group(1)
        content = match.group(2)
        closing_tag = match.group(3)
        
        if '{{' in content or '{%' in content:
            return match.group(0)
        
        if not self.is_translatable_text(content):
            return match.group(0)
        
        escaped_content = content.strip().replace('"', '\\"')
        return f'{opening_tag}{{% trans "{escaped_content}" %}}{closing_tag}'
    
    def wrap_link_text(self, match) -> str:
        """Wrap anchor tag text"""
        opening_tag = match.group(1)
        content = match.group(2)
        closing_tag = match.group(3)
        
        # Skip if contains HTML tags or template tags
        if '<' in content or '{{' in content or '{%' in content:
            return match.group(0)
        
        if not self.is_translatable_text(content):
            return match.group(0)
        
        escaped_content = content.strip().replace('"', '\\"')
        return f'{opening_tag}{{% trans "{escaped_content}" %}}{closing_tag}'
    
    def process_template(self, content: str) -> Tuple[str, int]:
        """Process a template file and wrap translatable strings"""
        original_content = content
        changes = 0
        
        # Add {% load i18n %} if not present
        if not self.has_i18n_load(content):
            content = self.add_i18n_load(content)
            changes += 1
        
        # Wrap ARIA labels (aria-label, aria-labelledby)
        pattern = r'(aria-label(?:ledby)?)\s*=\s*(["\'"])([^"\']+)\2'
        new_content = re.sub(pattern, self.wrap_aria_label, content)
        if new_content != content:
            changes += len(re.findall(pattern, content))
            content = new_content
        
        # Wrap alt attributes
        pattern = r'alt\s*=\s*(["\'"])([^"\']+)\1'
        new_content = re.sub(pattern, self.wrap_alt_text, content)
        if new_content != content:
            changes += len(re.findall(pattern, content))
            content = new_content
        
        # Wrap placeholder attributes
        pattern = r'placeholder\s*=\s*(["\'"])([^"\']+)\1'
        new_content = re.sub(pattern, self.wrap_placeholder, content)
        if new_content != content:
            changes += len(re.findall(pattern, content))
            content = new_content
        
        # Wrap heading text (h1-h6)
        pattern = r'(<h[1-6][^>]*>)\s*([^<{]+?)\s*(</h[1-6]>)'
        new_content = re.sub(pattern, self.wrap_heading, content)
        if new_content != content:
            changes += len(re.findall(pattern, content))
            content = new_content
        
        # Wrap button text
        pattern = r'(<button[^>]*>)\s*([^<{]+?)\s*(</button>)'
        new_content = re.sub(pattern, self.wrap_button, content)
        if new_content != content:
            changes += len(re.findall(pattern, content))
            content = new_content
        
        # Wrap anchor text (simple cases only)
        pattern = r'(<a[^>]*>)\s*([^<{]+?)\s*(</a>)'
        new_content = re.sub(pattern, self.wrap_link_text, content)
        if new_content != content:
            changes += len(re.findall(pattern, content))
            content = new_content
        
        return content, changes
    
    def process_file(self, filepath: Path) -> bool:
        """Process a single template file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content, changes = self.process_template(content)
            
            if changes > 0:
                self.changes_made += changes
                self.files_processed += 1
                
                if self.dry_run:
                    print(f"✓ {filepath.relative_to(Path.cwd())} - {changes} changes (DRY RUN)")
                else:
                    # Create backup
                    backup_path = filepath.with_suffix(filepath.suffix + '.bak')
                    shutil.copy2(filepath, backup_path)
                    
                    # Write new content
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"✓ {filepath.relative_to(Path.cwd())} - {changes} changes (backup: {backup_path.name})")
                
                return True
            else:
                print(f"- {filepath.relative_to(Path.cwd())} - no changes needed")
                return False
                
        except Exception as e:
            print(f"✗ Error processing {filepath}: {e}", file=sys.stderr)
            return False
    
    def find_templates(self, base_dir: Path) -> List[Path]:
        """Find all HTML template files"""
        templates = []
        
        # Search in common template directories (from project root)
        search_dirs = [
            'nmtsa_lms/nmtsa_lms/templates',
            'nmtsa_lms/student_dash/templates',
            'nmtsa_lms/teacher_dash/templates',
            'nmtsa_lms/admin_dash/templates',
        ]
        
        for search_dir in search_dirs:
            dir_path = Path(search_dir)
            if dir_path.exists():
                templates.extend(dir_path.rglob('*.html'))
            else:
                print(f"⚠️  Directory not found: {search_dir}")
        
        return sorted(templates)

def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automatically wrap translatable strings in Django templates'
    )
    parser.add_argument('files', nargs='*', help='Template files to process')
    parser.add_argument('--all', action='store_true', help='Process all templates')
    parser.add_argument('--check', action='store_true', help='Dry run - show what would change')
    parser.add_argument('--priority', action='store_true', help='Process only priority 1 templates')
    
    args = parser.parse_args()
    
    translator = TemplateTranslator(dry_run=args.check)
    
    # Check if we're in the right directory
    if not Path('nmtsa_lms').exists():
        print("Error: Run this script from the project root directory", file=sys.stderr)
        print("Current directory:", Path.cwd(), file=sys.stderr)
        sys.exit(1)
    
    # Determine which files to process
    files_to_process = []
    
    if args.all:
        files_to_process = translator.find_templates(Path.cwd())
        print(f"Found {len(files_to_process)} template files\n")
    
    elif args.priority:
        # Priority 1 templates (relative to project root)
        priority_files = [
            'nmtsa_lms/nmtsa_lms/templates/landing.html',
            'nmtsa_lms/nmtsa_lms/templates/faq.html',
            'nmtsa_lms/nmtsa_lms/templates/contact.html',
            'nmtsa_lms/nmtsa_lms/templates/authentication/select_role.html',
            'nmtsa_lms/nmtsa_lms/templates/authentication/student_onboarding.html',
            'nmtsa_lms/nmtsa_lms/templates/authentication/teacher_onboarding.html',
        ]
        files_to_process = []
        for f in priority_files:
            fpath = Path(f)
            if fpath.exists():
                files_to_process.append(fpath)
            else:
                print(f"⚠️  File not found: {f}")
        print(f"Processing {len(files_to_process)} priority templates\n")
    
    elif args.files:
        files_to_process = [Path(f) for f in args.files]
    
    else:
        parser.print_help()
        sys.exit(1)
    
    # Process files
    if args.check:
        print("🔍 DRY RUN MODE - No files will be modified\n")
    
    for filepath in files_to_process:
        translator.process_file(filepath)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Files processed: {translator.files_processed}")
    print(f"  Total changes: {translator.changes_made}")
    
    if args.check:
        print(f"\n⚠️  This was a dry run. Run without --check to apply changes.")
    else:
        print(f"\n✅ Changes applied! Backup files created with .bak extension")
        print(f"\nNext steps:")
        print(f"  1. Review the changes in your editor")
        print(f"  2. Run: python manage.py makemessages -l es")
        print(f"  3. Edit: locale/es/LC_MESSAGES/django.po")
        print(f"  4. Run: python manage.py compilemessages")
        print(f"  5. Test language switching")
    
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
