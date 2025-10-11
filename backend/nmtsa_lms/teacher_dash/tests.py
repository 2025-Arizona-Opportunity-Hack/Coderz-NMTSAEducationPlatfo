from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from authentication.models import TeacherProfile, User
from teacher_dash.models import Course, Module, Lesson


class TeacherDashboardTests(TestCase):
    def setUp(self) -> None:
        self.teacher = User.objects.create_user(
            username="teach1",
            email="teach@example.com",
            password="pass1234",
            role="teacher",
            onboarding_complete=True,
        )
        self.session_template = {
            "user_id": self.teacher.pk,
            "role": "teacher",
            "onboarding_complete": True,
        }

    def _login(self, extra=None) -> None:
        session = self.client.session
        session["user"] = {**self.session_template, **(extra or {})}
        session.save()

    def test_course_creation_creates_draft(self) -> None:
        self._login()
        response = self.client.post(
            reverse("teacher_create_course"),
            {"title": "Course A", "description": "Intro", "price": "10", "is_paid": True},
        )
        self.assertEqual(response.status_code, 302)
        course = Course.objects.get(title="Course A")
        self.assertFalse(course.is_published)
        self.assertTrue(course.is_paid)
        self.assertEqual(course.published_by, self.teacher)

    def test_add_module_and_lesson(self) -> None:
        self._login()
        course = Course.objects.create(
            title="Course B",
            description="Desc",
            price=0,
            published_by=self.teacher,
        )
        response = self.client.post(
            reverse("teacher_module_create", args=[course.pk]),
            {"title": "Module 1", "description": "Module desc"},
        )
        self.assertEqual(response.status_code, 302)
        module = Module.objects.get(title="Module 1")
        add_lesson_url = reverse("teacher_lesson_create", args=[course.pk, module.pk])
        response = self.client.post(
            add_lesson_url,
            {
                "title": "Lesson 1",
                "lesson_type": "blog",
                "duration": 5,
                "tags": "alpha",
                "content": "Body text",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Lesson.objects.filter(title="Lesson 1").exists())

    def test_blog_lesson_requires_duration(self) -> None:
        self._login()
        course = Course.objects.create(
            title="Course C",
            description="Desc",
            price=0,
            published_by=self.teacher,
        )
        module = Module.objects.create(title="Module B", description="Module desc")
        course.modules.add(module)
        add_lesson_url = reverse("teacher_lesson_create", args=[course.pk, module.pk])
        response = self.client.post(
            add_lesson_url,
            {
                "title": "Lesson Blog",
                "lesson_type": "blog",
                "duration": "",
                "tags": "alpha",
                "content": "Body text",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Lesson.objects.filter(title="Lesson Blog").exists())

    def test_video_lesson_requires_upload(self) -> None:
        self._login()
        course = Course.objects.create(
            title="Course Video",
            description="Desc",
            price=0,
            published_by=self.teacher,
        )
        module = Module.objects.create(title="Module V", description="Module desc")
        course.modules.add(module)
        add_lesson_url = reverse("teacher_lesson_create", args=[course.pk, module.pk])
        response = self.client.post(
            add_lesson_url,
            {
                "title": "Lesson Video",
                "lesson_type": "video",
                "tags": "media",
                "transcript": "Transcript text",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Lesson.objects.filter(title="Lesson Video").exists())

    def test_video_lesson_sets_duration_from_upload(self) -> None:
        self._login()
        course = Course.objects.create(
            title="Course Video 2",
            description="Desc",
            price=0,
            published_by=self.teacher,
        )
        module = Module.objects.create(title="Module VX", description="Module desc")
        course.modules.add(module)
        add_lesson_url = reverse("teacher_lesson_create", args=[course.pk, module.pk])
        video_file = SimpleUploadedFile("sample.mp4", b"fake-video", content_type="video/mp4")
        with patch("teacher_dash.views._extract_video_duration_minutes", return_value=(3, None)):
            response = self.client.post(
                add_lesson_url,
                {
                    "title": "Lesson Video 2",
                    "lesson_type": "video",
                    "tags": "media",
                    "transcript": "Transcript text",
                    "video_file": video_file,
                },
            )
        self.assertEqual(response.status_code, 302)
        lesson = Lesson.objects.get(title="Lesson Video 2")
        self.assertEqual(lesson.duration, 3)

    def test_publish_requires_verification(self) -> None:
        TeacherProfile.objects.create(user=self.teacher, verification_status="pending")
        self._login()
        course = Course.objects.create(
            title="Course Pending",
            description="Desc",
            price=0,
            published_by=self.teacher,
        )
        response = self.client.post(reverse("teacher_course_publish", args=[course.pk]))
        self.assertEqual(response.status_code, 302)
        course.refresh_from_db()
        self.assertFalse(course.is_published)
        self.assertTrue(course.is_submitted_for_review)

    def test_verified_teacher_publishes(self) -> None:
        TeacherProfile.objects.create(user=self.teacher, verification_status="approved")
        self._login()
        course = Course.objects.create(
            title="Course Publish",
            description="Desc",
            price=0,
            published_by=self.teacher,
        )
        response = self.client.post(reverse("teacher_course_publish", args=[course.pk]))
        self.assertEqual(response.status_code, 302)
        course.refresh_from_db()
        self.assertTrue(course.is_published)
        self.assertFalse(course.is_submitted_for_review)
