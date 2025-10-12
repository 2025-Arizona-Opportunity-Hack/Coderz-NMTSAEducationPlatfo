"""
Management command to sync all published courses to Supermemory
Run this to index existing courses for semantic search
"""
from django.core.management.base import BaseCommand
from teacher_dash.models import Course
from lms.course_memory import add_course_to_memory
from lms.supermemory_client import get_supermemory_client


class Command(BaseCommand):
    help = 'Sync all published courses to Supermemory for semantic search'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sync all courses including unpublished ones',
        )
        parser.add_argument(
            '--course-id',
            type=int,
            help='Sync a specific course by ID',
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting course synchronization to Supermemory...")
        
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
        
        # Get courses to sync
        if options['course_id']:
            courses = Course.objects.filter(id=options['course_id'])
            if not courses.exists():
                self.stdout.write(
                    self.style.ERROR(f'Course with ID {options["course_id"]} not found')
                )
                return
        elif options['all']:
            courses = Course.objects.all()
            self.stdout.write(f"Syncing ALL courses (including unpublished)...")
        else:
            courses = Course.objects.filter(
                is_published=True,
                admin_approved=True
            )
            self.stdout.write(f"Syncing published and approved courses...")
        
        success_count = 0
        error_count = 0
        
        for course in courses:
            self.stdout.write(f"  Syncing: {course.title}...", ending=' ')
            
            # Get modules for this course
            modules = course.modules.all()
            module_data = [
                {'title': m.title, 'description': m.description}
                for m in modules
            ]
            
            # Get tags
            tags = list(course.tags.names())
            
            # Prepare course data
            course_data = {
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'tags': tags,
                'modules': module_data,
                'is_paid': course.is_paid,
                'is_published': course.is_published,
            }
            
            # Add to memory
            if add_course_to_memory(course_data):
                self.stdout.write(self.style.SUCCESS('✓'))
                success_count += 1
            else:
                self.stdout.write(self.style.ERROR('✗'))
                error_count += 1
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'✓ Successfully synced: {success_count} courses')
        )
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to sync: {error_count} courses')
            )
        
        self.stdout.write(
            '\n💡 Courses are now searchable via semantic search in the chatbot!'
        )
