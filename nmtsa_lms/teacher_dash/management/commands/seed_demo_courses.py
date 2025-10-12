from django.core.management.base import BaseCommand

from authentication.models import User
from teacher_dash.models import Course, Module, Lesson


class Command(BaseCommand):
    help = "Create a demo teacher with sample course, module, and lesson data."

    def handle(self, *args, **options):
        teacher, _ = User.objects.get_or_create(
            email="demo-teacher@example.com",
            defaults={
                "username": "demo-teacher",
                "role": "teacher",
                "onboarding_complete": True,
            },
        )

        course, created_course = Course.objects.get_or_create(
            title="Demo Neurologic Music Therapy",
            defaults={
                "description": "An introductory course showcasing the LMS instructor workflow.",
                "price": 0,
                "published_by": teacher,
            },
        )

        if created_course:
            self.stdout.write(self.style.SUCCESS("Created sample course."))

        module, created_module = Module.objects.get_or_create(
            title="Foundations",
            defaults={"description": "Core principles and framework."},
        )
        if created_module:
            course.modules.add(module)

        lesson, created_lesson = Lesson.objects.get_or_create(
            title="Welcome",
            defaults={
                "lesson_type": "blog",
                "duration": 10,
            },
        )
        if created_lesson:
            module.lessons.add(lesson)

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
