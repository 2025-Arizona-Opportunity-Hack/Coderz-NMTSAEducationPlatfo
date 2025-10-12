from __future__ import annotations

from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django_ckeditor_5.widgets import CKEditor5Widget
from taggit.forms import TagField

from .models import Course, Module, Lesson, VideoLesson, BlogLesson, PDFLesson, DiscussionPost


class CourseForm(forms.ModelForm):
    tags = TagField(required=False, help_text="Comma separated tags", label="Tags")

    class Meta:
        model = Course
        fields = ["title", "description", "price", "is_paid"]
        widgets = {
            "description": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, 
                config_name='extends'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["tags"].initial = ", ".join(self.instance.tags.names())

    def clean(self):
        cleaned = super().clean()
        price = cleaned.get("price")
        # Automatically determine is_paid based on price value
        if price is None or price <= 0:
            # Free course
            cleaned["price"] = 0
            cleaned["is_paid"] = False
        else:
            # Paid course
            cleaned["is_paid"] = True

        return cleaned

    def save(self, commit: bool = True, teacher=None):
        course = super().save(commit=False)
        if teacher is not None:
            course.published_by = teacher
        if commit:
            course.save()
            if "tags" in self.cleaned_data:
                course.tags.set(self.cleaned_data["tags"])
        return course


class ModuleForm(forms.ModelForm):
    tags = TagField(required=False, help_text="Comma separated tags", label="Tags")

    class Meta:
        model = Module
        fields = ["title", "description"]
        widgets = {
            "description": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, 
                config_name='extends'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["tags"].initial = ", ".join(self.instance.tags.names())

    def save(self, commit: bool = True):
        module = super().save(commit=commit)
        if commit and "tags" in self.cleaned_data:
            module.tags.set(self.cleaned_data["tags"])
        return module


class LessonForm(forms.ModelForm):
    tags = TagField(required=False, help_text="Comma separated tags", label="Tags")

    class Meta:
        model = Lesson
        fields = ["title", "lesson_type", "duration"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pending_tags: Any | None = None
        if self.instance and self.instance.pk:
            self.fields["tags"].initial = ", ".join(self.instance.tags.names())
        self.fields["duration"].required = False
        self.fields["duration"].help_text = "Required for blog/PDF lessons. Video lessons will auto-calculate."

    def save(self, commit: bool = True):
        lesson = super().save(commit=commit)
        if "tags" in self.cleaned_data:
            if commit:
                lesson.tags.set(self.cleaned_data["tags"])
            else:
                self._pending_tags = self.cleaned_data["tags"]
        return lesson

    def save_m2m(self) -> None:
        super().save_m2m()
        if self._pending_tags is not None:
            self.instance.tags.set(self._pending_tags)
            self._pending_tags = None

    def clean(self):
        cleaned = super().clean()
        lesson_type = cleaned.get("lesson_type")
        duration = cleaned.get("duration")
        if lesson_type in ("blog", "pdf") and not duration:
            raise ValidationError({"duration": f"Duration is required for {lesson_type} lessons."})
        if lesson_type in ("blog", "pdf") and duration is not None and duration <= 0:
            raise ValidationError({"duration": "Duration must be a positive number."})
        if lesson_type == "video":
            cleaned["duration"] = None
        return cleaned


class VideoLessonForm(forms.ModelForm):
    video_file = forms.FileField(required=False)

    class Meta:
        model = VideoLesson
        fields = ["video_file", "transcript", "description"]
        widgets = {
            "transcript": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, 
                config_name='extends'
            ),
            "description": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, 
                config_name='extends'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        has_existing = bool(self.instance and getattr(self.instance, "video_file", None))
        self.fields["video_file"].required = not has_existing


class BlogLessonForm(forms.ModelForm):
    images = forms.ImageField(required=False)

    class Meta:
        model = BlogLesson
        fields = ["content", "images"]
        widgets = {
            "content": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, 
                config_name='extends'
            ),
        }


class PDFLessonForm(forms.ModelForm):
    pdf_file = forms.FileField(required=False)

    class Meta:
        model = PDFLesson
        fields = ["pdf_file", "description"]
        widgets = {
            "description": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, 
                config_name='extends'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        has_existing = bool(self.instance and getattr(self.instance, "pdf_file", None))
        self.fields["pdf_file"].required = not has_existing
        self.fields["pdf_file"].help_text = "Upload a PDF file (max 50MB, .pdf only)"

    def clean_pdf_file(self):
        pdf_file = self.cleaned_data.get("pdf_file")
        if pdf_file:
            # Check file extension
            if not pdf_file.name.lower().endswith('.pdf'):
                raise ValidationError("Only PDF files are allowed.")

            # Check file size (50MB max)
            max_size = 50 * 1024 * 1024  # 50MB in bytes
            if pdf_file.size > max_size:
                raise ValidationError(f"PDF file size cannot exceed 50MB. Current size: {pdf_file.size / (1024 * 1024):.2f}MB")

        return pdf_file


class DiscussionPostForm(forms.ModelForm):
    """Form for creating and editing discussion posts"""

    class Meta:
        model = DiscussionPost
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Share your thoughts, ask a question, or start a discussion...",
            }),
        }
        labels = {
            "content": "Your message",
        }

    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()

        # Minimum length validation
        if len(content) < 10:
            raise ValidationError("Your post must be at least 10 characters long.")

        # Maximum length validation
        if len(content) > 2000:
            raise ValidationError("Your post must be no more than 2000 characters long.")

        # XSS protection handled by CKEditor
        return content


class DiscussionReplyForm(forms.ModelForm):
    """Form for replying to discussion posts - identical to post form but visually distinct"""

    class Meta:
        model = DiscussionPost
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Write your reply...",
            }),
        }
        labels = {
            "content": "Your reply",
        }

    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()

        # Minimum length validation
        if len(content) < 10:
            raise ValidationError("Your reply must be at least 10 characters long.")

        # Maximum length validation
        if len(content) > 2000:
            raise ValidationError("Your reply must be no more than 2000 characters long.")

        # XSS protection handled by CKEditor
        return content