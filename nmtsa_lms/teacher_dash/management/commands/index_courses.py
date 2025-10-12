"""
Django management command to bulk index courses to Supermemory
Usage: python manage.py index_courses [--full] [--published-only]
"""
import logging
from django.core.management.base import BaseCommand
from django.db import transaction

from teacher_dash.models import Course, Module, Lesson
from lms.supermemory_client import get_supermemory_client
from lms.course_indexer import (
    build_course_document,
    build_module_document,
    build_lesson_document,
    get_course_from_module,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Bulk index courses, modules, and lessons to Supermemory for search'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Re-index all courses (otherwise only indexes unpublished courses)',
        )
        parser.add_argument(
            '--published-only',
            action='store_true',
            help='Only index published courses',
        )
        parser.add_argument(
            '--course-id',
            type=int,
            help='Index a specific course by ID',
        )
        parser.add_argument(
            '--course-slug',
            type=str,
            help='Index a specific course by slug',
        )

    def handle(self, *args, **options):
        """Main command handler"""
        client = get_supermemory_client()

        if not client:
            self.stdout.write(
                self.style.ERROR(
                    'Supermemory client not available. '
                    'Check SUPERMEMORY_API_KEY in environment.'
                )
            )
            return

        full_reindex = options['full']
        published_only = options['published_only']
        course_id = options.get('course_id')
        course_slug = options.get('course_slug')

        # Build queryset
        if course_id:
            courses = Course.objects.filter(id=course_id)
        elif course_slug:
            courses = Course.objects.filter(slug=course_slug)
        else:
            courses = Course.objects.all()

            if published_only:
                courses = courses.filter(is_published=True)

        course_count = courses.count()

        if course_count == 0:
            self.stdout.write(self.style.WARNING('No courses found to index.'))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'\nStarting indexing of {course_count} course(s)...\n'
            )
        )

        # Statistics
        stats = {
            'courses_indexed': 0,
            'courses_failed': 0,
            'modules_indexed': 0,
            'modules_failed': 0,
            'lessons_indexed': 0,
            'lessons_failed': 0,
        }

        # Index each course
        for i, course in enumerate(courses, 1):
            self.stdout.write(
                f'[{i}/{course_count}] Indexing course: {course.title} (slug: {course.slug})'
            )

            # Skip unpublished courses unless doing full reindex
            if not course.is_published and not full_reindex:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Skipping unpublished course: {course.title}'
                    )
                )
                continue

            # Index the course
            success = self.index_course(client, course)
            if success:
                stats['courses_indexed'] += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Indexed course: {course.title}')
                )
            else:
                stats['courses_failed'] += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Failed to index course: {course.title}')
                )

            # Index all modules for this course
            for module in course.modules.all():
                success = self.index_module(client, module, course)
                if success:
                    stats['modules_indexed'] += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'    ✓ Indexed module: {module.title}')
                    )
                else:
                    stats['modules_failed'] += 1
                    self.stdout.write(
                        self.style.ERROR(f'    ✗ Failed to index module: {module.title}')
                    )

                # Index all lessons for this module
                for lesson in module.lessons.all():
                    success = self.index_lesson(client, lesson, module, course)
                    if success:
                        stats['lessons_indexed'] += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'      ✓ Indexed lesson: {lesson.title}'
                            )
                        )
                    else:
                        stats['lessons_failed'] += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'      ✗ Failed to index lesson: {lesson.title}'
                            )
                        )

        # Print summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('Indexing Complete'))
        self.stdout.write('=' * 60)
        self.stdout.write(
            f"\nCourses:  {stats['courses_indexed']} indexed, {stats['courses_failed']} failed"
        )
        self.stdout.write(
            f"Modules:  {stats['modules_indexed']} indexed, {stats['modules_failed']} failed"
        )
        self.stdout.write(
            f"Lessons:  {stats['lessons_indexed']} indexed, {stats['lessons_failed']} failed"
        )
        self.stdout.write(
            f"\nTotal:    {stats['courses_indexed'] + stats['modules_indexed'] + stats['lessons_indexed']} indexed\n"
        )

        if (
            stats['courses_failed'] > 0
            or stats['modules_failed'] > 0
            or stats['lessons_failed'] > 0
        ):
            self.stdout.write(
                self.style.WARNING(
                    'Some items failed to index. Check logs for details.'
                )
            )

    def index_course(self, client, course):
        """Index a single course"""
        try:
            if not course.is_published:
                return True  # Skip but count as success

            content, metadata = build_course_document(course)
            result = client.index_course(content, metadata)
            return result is not None
        except Exception as e:
            logger.error(f'Error indexing course {course.slug}: {e}')
            return False

    def index_module(self, client, module, course):
        """Index a single module"""
        try:
            if not course.is_published:
                return True  # Skip but count as success

            content, metadata = build_module_document(module, course)
            result = client.index_module(content, metadata)
            return result is not None
        except Exception as e:
            logger.error(f'Error indexing module {module.slug}: {e}')
            return False

    def index_lesson(self, client, lesson, module, course):
        """Index a single lesson"""
        try:
            if not course.is_published:
                return True  # Skip but count as success

            content, metadata = build_lesson_document(lesson, module, course)
            result = client.index_lesson(content, metadata)
            return result is not None
        except Exception as e:
            logger.error(f'Error indexing lesson {lesson.slug}: {e}')
            return False
