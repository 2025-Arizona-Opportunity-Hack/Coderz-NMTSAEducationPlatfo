"""
Management command to generate translation files for all configured languages.
Usage: python manage.py generate_translations
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Generate translation files (.po) for all configured languages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--compile',
            action='store_true',
            help='Compile translation files after generation',
        )
        parser.add_argument(
            '--js',
            action='store_true',
            help='Also generate JavaScript translation files',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌍 Generating translation files for NMTSA LMS'))
        self.stdout.write('')

        # Get configured languages from settings
        languages = [lang_code for lang_code, lang_name in settings.LANGUAGES]
        
        self.stdout.write(f'Configured languages: {", ".join(languages)}')
        self.stdout.write('')

        # Generate Django template and Python translations
        self.stdout.write(self.style.HTTP_INFO('📝 Generating Django translations...'))
        for lang_code in languages:
            if lang_code == 'en':
                self.stdout.write(f'  • Skipping {lang_code} (source language)')
                continue
            
            try:
                self.stdout.write(f'  • Generating for {lang_code}...')
                call_command('makemessages', 
                           locale=[lang_code],
                           ignore=['node_modules', 'staticfiles', '.venv', 'venv'],
                           verbosity=0)
                self.stdout.write(self.style.SUCCESS(f'    ✓ Created locale/{lang_code}/LC_MESSAGES/django.po'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'    ✗ Error: {str(e)}'))

        # Generate JavaScript translations if requested
        if options['js']:
            self.stdout.write('')
            self.stdout.write(self.style.HTTP_INFO('📝 Generating JavaScript translations...'))
            for lang_code in languages:
                if lang_code == 'en':
                    continue
                
                try:
                    self.stdout.write(f'  • Generating JS for {lang_code}...')
                    call_command('makemessages',
                               locale=[lang_code],
                               domain='djangojs',
                               ignore=['node_modules', 'staticfiles', '.venv', 'venv'],
                               verbosity=0)
                    self.stdout.write(self.style.SUCCESS(f'    ✓ Created locale/{lang_code}/LC_MESSAGES/djangojs.po'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    ✗ Error: {str(e)}'))

        # Compile translations if requested
        if options['compile']:
            self.stdout.write('')
            self.stdout.write(self.style.HTTP_INFO('🔨 Compiling translation files...'))
            try:
                call_command('compilemessages', verbosity=0)
                self.stdout.write(self.style.SUCCESS('  ✓ All translations compiled successfully'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Compilation error: {str(e)}'))

        # Print next steps
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Translation file generation complete!'))
        self.stdout.write('')
        self.stdout.write('📋 Next steps:')
        self.stdout.write('  1. Edit the .po files in the locale/ directory')
        self.stdout.write('  2. Fill in the msgstr values with translations')
        self.stdout.write('  3. Run: python manage.py compilemessages')
        self.stdout.write('  4. Restart the development server')
        self.stdout.write('')
        self.stdout.write('📚 Documentation: docs/LOCALIZATION_GUIDE.md')
