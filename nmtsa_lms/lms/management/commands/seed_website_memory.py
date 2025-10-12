"""
Management command to seed website information into Supermemory
Run this after setting up Supermemory to populate initial context
"""
from django.core.management.base import BaseCommand
from lms.course_memory import add_website_info_to_memory
from lms.supermemory_client import get_supermemory_client


class Command(BaseCommand):
    help = 'Seed NMTSA LMS website information into Supermemory for chatbot context'

    def handle(self, *args, **options):
        self.stdout.write("Starting website info seeding to Supermemory...")
        
        # Check if Supermemory is configured
        client = get_supermemory_client()
        if not client:
            self.stdout.write(
                self.style.ERROR(
                    'Supermemory is not configured. Please set SUPERMEMORY_API_KEY '
                    'and OPENAI_API_KEY in your environment or .env file.'
                )
            )
            return
        
        # Add website info
        self.stdout.write("Adding website information to memory...")
        success = add_website_info_to_memory()
        
        if success:
            self.stdout.write(
                self.style.SUCCESS(
                    '✓ Successfully seeded website information to Supermemory!'
                )
            )
            self.stdout.write(
                '\nThe chatbot now has context about:'
                '\n  - NMTSA LMS platform features'
                '\n  - User roles and authentication'
                '\n  - Course structure and enrollment'
                '\n  - Getting started guide'
            )
            self.stdout.write(
                '\n💡 Tip: Run "python manage.py sync_courses_to_memory" to add course data'
            )
        else:
            self.stdout.write(
                self.style.ERROR('✗ Failed to seed website information')
            )
