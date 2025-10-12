from __future__ import annotations

import math
import os
import tempfile
from pathlib import Path
from typing import Any, Tuple

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import mail_admins
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse, FileResponse
from django.shortcuts import get_object_or_404, redirect, render
import uuid

from authentication.decorators import (
    onboarding_complete_required,
    teacher_required,
)
from authentication.models import TeacherProfile
from lms.models import CompletedLesson
from teacher_dash.forms import (
    BlogLessonForm,
    CourseForm,
    LessonForm,
    ModuleForm,
    VideoLessonForm,
    DiscussionPostForm,
    DiscussionReplyForm,
)
from teacher_dash.models import BlogLesson, Course, Lesson, Module, VideoLesson, DiscussionPost

User = get_user_model()


def _get_logged_in_teacher(request: HttpRequest) -> Any:
    session_user = request.session.get("user")
    if not session_user:
        raise ValueError("Missing session user")
    user_id = session_user.get("user_id")
    return get_object_or_404(User, id=user_id)


def _check_teacher_approval(request: HttpRequest) -> bool:
    """
    Check if the logged-in teacher is approved to create/edit courses.
    If not approved, adds an error message and redirects to verification status.
    Returns True if approved, False if not approved (and redirect handled).
    """
    teacher = _get_logged_in_teacher(request)
    teacher_profile = TeacherProfile.objects.filter(user=teacher).first()
    
    if not teacher_profile or teacher_profile.verification_status != "approved":
        messages.error(
            request,
            "Your teacher profile isn't approved yet. Please wait for verification to create or edit courses."
        )
        return False
    
    return True


def _handle_course_content_change(course: Course) -> str:
    """
    Handle the workflow when content changes are made to a published course.
    Unpublishes the course and resubmits for admin review while preserving enrollments.
    Returns a success message for the user.
    """
    if course.is_published:
        course.is_published = False
        course.is_submitted_for_review = True
        course.admin_approved = False
        course.save()
        return "Changes saved. The course is now unpublished and resubmitted for admin review. Enrollments and discussions remain intact."
    return "Changes saved successfully."


def uuid_gen():
    return str(uuid.uuid4())


@teacher_required
@onboarding_complete_required
def dashboard(request: HttpRequest) -> HttpResponse:
    teacher = _get_logged_in_teacher(request)
    courses = Course.objects.filter(published_by=teacher).prefetch_related("modules", "modules__lessons")

    published = courses.filter(is_published=True)
    drafts = courses.filter(is_published=False)

    teacher_profile = TeacherProfile.objects.filter(user=teacher).first()
    is_teacher_approved = teacher_profile and teacher_profile.verification_status == "approved"

    # Group courses by review status
    awaiting_review = drafts.filter(is_submitted_for_review=True, admin_approved=False)
    approved_not_published = drafts.filter(admin_approved=True, is_submitted_for_review=True)
    not_submitted = drafts.filter(is_submitted_for_review=False)

    context = {
        "published_courses": published,
        "draft_courses": drafts,
        "course_count": courses.count(),
        "draft_count": drafts.count(),
        "published_count": published.count(),
        "verification_status": getattr(teacher_profile, "verification_status", "pending"),
        "is_teacher_approved": is_teacher_approved,
        "awaiting_review_count": awaiting_review.count(),
        "approved_not_published_count": approved_not_published.count(),
        "not_submitted_count": not_submitted.count(),
    }
    return render(request, "teacher_dash/dashboard.html", context)


@teacher_required
@onboarding_complete_required
def courses(request: HttpRequest) -> HttpResponse:
    return dashboard(request)


@teacher_required
@onboarding_complete_required
def course_create(request: HttpRequest) -> HttpResponse:
    if not _check_teacher_approval(request):
        return redirect("teacher_verification_status")
        
    teacher = _get_logged_in_teacher(request)

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(teacher=teacher)
            messages.success(request, "Course created. You can now add modules and lessons.")
            return redirect("teacher_course_detail", course_id=course.pk)
    else:
        form = CourseForm()

    teacher_profile = TeacherProfile.objects.filter(user=teacher).first()
    is_teacher_approved = teacher_profile and teacher_profile.verification_status == "approved"
    
    return render(request, "teacher_dash/course_form.html", {"form": form, "is_teacher_approved": is_teacher_approved})


@teacher_required
@onboarding_complete_required
def course_detail(request: HttpRequest, course_id: int) -> HttpResponse:
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(
        Course.objects.prefetch_related("modules", "modules__lessons"),
        pk=course_id,
        published_by=teacher,
    )
    teacher_profile = TeacherProfile.objects.filter(user=teacher).first()
    is_teacher_approved = teacher_profile and teacher_profile.verification_status == "approved"
    
    module_form = ModuleForm()
    return render(
        request,
        "teacher_dash/course_detail.html",
        {
            "course": course,
            "module_form": module_form,
            "is_teacher_approved": is_teacher_approved,
        },
    )


@teacher_required
@onboarding_complete_required
def course_edit(request: HttpRequest, course_id: int) -> HttpResponse:
    if not _check_teacher_approval(request):
        return redirect("teacher_verification_status")
        
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            success_message = _handle_course_content_change(course)
            messages.success(request, success_message)
            return redirect("teacher_course_detail", course_id=course.pk)
    else:
        form = CourseForm(instance=course)

    teacher_profile = TeacherProfile.objects.filter(user=teacher).first()
    is_teacher_approved = teacher_profile and teacher_profile.verification_status == "approved"
    
    return render(request, "teacher_dash/course_form.html", {"form": form, "course": course, "is_teacher_approved": is_teacher_approved})


@teacher_required
@onboarding_complete_required
def course_delete(request: HttpRequest, course_id: int) -> HttpResponse:
    if not _check_teacher_approval(request):
        return redirect("teacher_verification_status")
        
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted.")
        return redirect("teacher_dashboard")
    return redirect("teacher_course_detail", course_id=course.pk)


@teacher_required
@onboarding_complete_required
def module_create(request: HttpRequest, course_id: int) -> HttpResponse:
    if not _check_teacher_approval(request):
        return redirect("teacher_verification_status")
        
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)

    if request.method == "POST":
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save()
            course.modules.add(module)
            success_message = _handle_course_content_change(course)
            messages.success(request, success_message)
        else:
            messages.error(request, "Please fix the errors below.")
            return render(
                request,
                "teacher_dash/course_detail.html",
                {"course": course, "module_form": form},
            )

    return redirect("teacher_course_detail", course_id=course.pk)


@teacher_required
@onboarding_complete_required
def module_edit(request: HttpRequest, course_id: int, module_id: int) -> HttpResponse:
    if not _check_teacher_approval(request):
        return redirect("teacher_verification_status")
        
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)
    module = get_object_or_404(course.modules, pk=module_id)

    if request.method == "POST":
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            success_message = _handle_course_content_change(course)
            messages.success(request, success_message)
            return redirect("teacher_module_detail", course_id=course.pk, module_id=module.pk)
    else:
        form = ModuleForm(instance=module)

    teacher_profile = TeacherProfile.objects.filter(user=teacher).first()
    is_teacher_approved = teacher_profile and teacher_profile.verification_status == "approved"

    return render(
        request,
        "teacher_dash/module_form.html",
        {"form": form, "course": course, "module": module, "is_teacher_approved": is_teacher_approved},
    )


@teacher_required
@onboarding_complete_required
def module_detail(request: HttpRequest, course_id: int, module_id: int) -> HttpResponse:
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)
    module = get_object_or_404(course.modules.prefetch_related("lessons"), pk=module_id)
    teacher_profile = TeacherProfile.objects.filter(user=teacher).first()
    is_teacher_approved = teacher_profile and teacher_profile.verification_status == "approved"
    
    lesson_form = LessonForm()
    video_form = VideoLessonForm()
    blog_form = BlogLessonForm()
    return render(
        request,
        "teacher_dash/module_detail.html",
        {
            "course": course,
            "module": module,
            "lesson_form": lesson_form,
            "video_form": video_form,
            "blog_form": blog_form,
            "is_teacher_approved": is_teacher_approved,
        },
    )


@teacher_required
@onboarding_complete_required
def module_delete(request: HttpRequest, course_id: int, module_id: int) -> HttpResponse:
    if not _check_teacher_approval(request):
        return redirect("teacher_verification_status")
        
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)
    module = get_object_or_404(course.modules, pk=module_id)
    if request.method == "POST":
        course.modules.remove(module)
        module.delete()
        success_message = _handle_course_content_change(course)
        messages.success(request, success_message)
    return redirect("teacher_course_detail", course_id=course.pk)


def _get_lesson_forms(request: HttpRequest, instance: Lesson | None = None) -> Tuple[LessonForm, VideoLessonForm, BlogLessonForm]:
    lesson_form = LessonForm(request.POST or None, instance=instance)
    video_form = VideoLessonForm(request.POST or None, request.FILES or None, instance=getattr(instance, "video", None))
    blog_form = BlogLessonForm(request.POST or None, request.FILES or None, instance=getattr(instance, "blog", None))
    return lesson_form, video_form, blog_form


def _extract_video_duration_minutes(file_field: Any) -> Tuple[int | None, str | None]:
    if not file_field:
        return None, "Video file is required."
    try:
        from moviepy import VideoFileClip  # type: ignore[import]
    except ImportError:
        return None, "Video duration detection requires moviepy. Please contact the administrator."

    temp_path: str | None = None
    video_path: str | None = None
    try:
        if hasattr(file_field, "path"):
            video_path = file_field.path
        elif hasattr(file_field, "temporary_file_path"):
            video_path = file_field.temporary_file_path()
        else:
            suffix = Path(getattr(file_field, "name", "")).suffix or ".mp4"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                for chunk in file_field.chunks():
                    tmp.write(chunk)
                temp_path = tmp.name
            video_path = temp_path
            if hasattr(file_field, "seek"):
                file_field.seek(0)

        if not video_path:
            return None, "Unable to access the uploaded video file."

        with VideoFileClip(video_path) as clip:
            duration_seconds = clip.duration

        if duration_seconds is None:
            return None, "Unable to read video duration."
        return max(1, math.ceil(duration_seconds / 60)), None
    except Exception:
        return None, "Unable to process the video file."
    finally:
        if temp_path:
            try:
                os.remove(temp_path)
            except OSError:
                pass


@teacher_required
@onboarding_complete_required
def lesson_create(request: HttpRequest, course_id: int, module_id: int) -> HttpResponse:
    if not _check_teacher_approval(request):
        return redirect("teacher_verification_status")
        
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)
    module = get_object_or_404(course.modules, pk=module_id)

    lesson_form, video_form, blog_form = _get_lesson_forms(request)

    if request.method == "POST":
        lesson_valid = lesson_form.is_valid()
        lesson_type = lesson_form.cleaned_data.get("lesson_type") if lesson_valid else None
        video_valid = blog_valid = True
        video_duration: int | None = None
        extraction_error: str | None = None

        if lesson_valid and lesson_type == "video":
            video_valid = video_form.is_valid()
            if video_valid:
                file_for_duration = video_form.cleaned_data.get("video_file") or getattr(video_form.instance, "video_file", None)
                video_duration, extraction_error = _extract_video_duration_minutes(file_for_duration)
                if video_duration is None:
                    video_form.add_error(
                        "video_file",
                        extraction_error or "Unable to determine video duration. Please upload a valid video file.",
                    )
                    video_valid = False
                else:
                    # Rename uploaded file to a unique UUID-based filename while preserving the extension
                    uploaded_file = file_for_duration
                    try:
                        ext = Path(getattr(uploaded_file, "name", "")).suffix or ".mp4"
                        new_video_filename = f"{uuid_gen()}{ext}"
                        # UploadedFile.name is writable; update so the storage will use the new name
                        uploaded_file.name = new_video_filename
                        # Ensure cleaned_data points to the renamed file object
                        if "video_file" in video_form.cleaned_data and video_form.cleaned_data["video_file"] is uploaded_file:
                            video_form.cleaned_data["video_file"].name = new_video_filename
                    except Exception:
                        # If renaming fails for any reason, continue with the original filename
                        pass
        elif lesson_valid and lesson_type == "blog":
            blog_valid = blog_form.is_valid()

        if lesson_valid and video_valid and blog_valid and lesson_type:
            with transaction.atomic():
                lesson = lesson_form.save(commit=False)
                if lesson_type == "video":
                    lesson.duration = video_duration
                else:
                    lesson.duration = lesson_form.cleaned_data.get("duration")
                lesson.save()
                lesson_form.save_m2m()
                module.lessons.add(lesson)

                if lesson_type == "video":
                    BlogLesson.objects.filter(lesson=lesson).delete()
                    video = video_form.save(commit=False)
                    video.lesson = lesson
                    video.save()
                else:
                    VideoLesson.objects.filter(lesson=lesson).delete()
                    blog = blog_form.save(commit=False)
                    blog.lesson = lesson
                    blog.save()
            success_message = _handle_course_content_change(course)
            messages.success(request, success_message)
            return redirect("teacher_module_detail", course_id=course.pk, module_id=module.pk)

        messages.error(request, "Please correct the errors below.")
        return render(
            request,
            "teacher_dash/module_detail.html",
            {
                "course": course,
                "module": module,
                "lesson_form": lesson_form,
                "video_form": video_form,
                "blog_form": blog_form,
            },
            status=400,
        )

    teacher_profile = TeacherProfile.objects.filter(user=teacher).first()
    is_teacher_approved = teacher_profile and teacher_profile.verification_status == "approved"

    return render(
        request,
        "teacher_dash/lesson_form.html",
        {
            "course": course,
            "module": module,
            "lesson_form": lesson_form,
            "video_form": video_form,
            "blog_form": blog_form,
            "is_teacher_approved": is_teacher_approved,
        },
    )


@teacher_required
@onboarding_complete_required
def lesson_edit(request: HttpRequest, course_id: int, module_id: int, lesson_id: int) -> HttpResponse:
    if not _check_teacher_approval(request):
        return redirect("teacher_verification_status")
        
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)
    module = get_object_or_404(course.modules, pk=module_id)
    lesson = get_object_or_404(module.lessons, pk=lesson_id)

    lesson_form, video_form, blog_form = _get_lesson_forms(request, instance=lesson)

    if request.method == "POST":
        lesson_valid = lesson_form.is_valid()
        lesson_type = lesson_form.cleaned_data.get("lesson_type") if lesson_valid else None
        video_valid = blog_valid = True
        video_duration: int | None = None
        extraction_error: str | None = None

        if lesson_valid and lesson_type == "video":
            video_valid = video_form.is_valid()
            if video_valid:
                file_for_duration = video_form.cleaned_data.get("video_file") or getattr(video_form.instance, "video_file", None)
                video_duration, extraction_error = _extract_video_duration_minutes(file_for_duration)
                if video_duration is None:
                    video_form.add_error("video_file", extraction_error or "Unable to determine video duration. Please upload a valid video file.")
                    video_valid = False
        elif lesson_valid and lesson_type == "blog":
            blog_valid = blog_form.is_valid()

        if lesson_valid and video_valid and blog_valid and lesson_type:
            with transaction.atomic():
                lesson = lesson_form.save(commit=False)
                if lesson_type == "video":
                    lesson.duration = video_duration
                else:
                    lesson.duration = lesson_form.cleaned_data.get("duration")
                lesson.save()
                lesson_form.save_m2m()

                if lesson_type == "video":
                    BlogLesson.objects.filter(lesson=lesson).delete()
                    video = video_form.save(commit=False)
                    video.lesson = lesson
                    video.save()
                else:
                    VideoLesson.objects.filter(lesson=lesson).delete()
                    blog = blog_form.save(commit=False)
                    blog.lesson = lesson
                    blog.save()
            success_message = _handle_course_content_change(course)
            messages.success(request, success_message)
            return redirect("teacher_module_detail", course_id=course.pk, module_id=module.pk)

        messages.error(request, "Please correct the errors below.")

    teacher_profile = TeacherProfile.objects.filter(user=teacher).first()
    is_teacher_approved = teacher_profile and teacher_profile.verification_status == "approved"

    return render(
        request,
        "teacher_dash/lesson_form.html",
        {
            "course": course,
            "module": module,
            "lesson_form": lesson_form,
            "video_form": video_form,
            "blog_form": blog_form,
            "lesson": lesson,
            "is_teacher_approved": is_teacher_approved,
        },
    )


@teacher_required
@onboarding_complete_required
def lesson_delete(request: HttpRequest, course_id: int, module_id: int, lesson_id: int) -> HttpResponse:
    if not _check_teacher_approval(request):
        return redirect("teacher_verification_status")
        
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)
    module = get_object_or_404(course.modules, pk=module_id)
    lesson = get_object_or_404(module.lessons, pk=lesson_id)

    if request.method == "POST":
        module.lessons.remove(lesson)
        lesson.delete()
        success_message = _handle_course_content_change(course)
        messages.success(request, success_message)
    return redirect("teacher_module_detail", course_id=course.pk, module_id=module.pk)


@teacher_required
@onboarding_complete_required
def course_preview(request: HttpRequest, course_id: int) -> HttpResponse:
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)

    modules = course.modules.prefetch_related("lessons", "lessons__video", "lessons__blog")
    context = {
        "course": course,
        "modules": modules,
    }
    return render(request, "teacher_dash/course_preview.html", context)


@onboarding_complete_required
def lesson_preview(request: HttpRequest, course_id: int, module_id: int, lesson_id: int) -> JsonResponse:
    """
    Preview lesson content - accessible by course owner (teacher) or admins
    """
    # Get current user
    session_user = request.session.get("user")
    if not session_user:
        return JsonResponse({"error": "Authentication required"}, status=401)

    user_id = session_user.get("user_id")
    user_role = session_user.get("role")
    user = get_object_or_404(User, id=user_id)

    # Fetch course - admins can access any course, teachers only their own
    if user_role == "admin":
        course = get_object_or_404(Course, pk=course_id)
    elif user_role == "teacher":
        course = get_object_or_404(Course, pk=course_id, published_by=user)
    else:
        return JsonResponse({"error": "Access denied"}, status=403)

    module = get_object_or_404(course.modules, pk=module_id)
    lesson = get_object_or_404(module.lessons, pk=lesson_id)

    response_data = {
        "id": lesson.id,
        "title": lesson.title,
        "lesson_type": lesson.lesson_type,
        "duration": lesson.duration,
    }

    if lesson.lesson_type == "video":
        try:
            video = lesson.video
            if video.video_file:
                video_url = f"/teacher/videos/{video.video_file.name}"
                response_data["video_url"] = request.build_absolute_uri(video_url)
            else:
                response_data["video_url"] = None
            response_data["transcript"] = video.transcript
        except VideoLesson.DoesNotExist:
            response_data["video_url"] = None
            response_data["transcript"] = None
    else:
        try:
            blog = lesson.blog
            response_data["content"] = blog.content
            response_data["image_url"] = request.build_absolute_uri(blog.images.url) if blog.images else None
        except BlogLesson.DoesNotExist:
            response_data["content"] = None
            response_data["image_url"] = None

    return JsonResponse(response_data)


@teacher_required
@onboarding_complete_required
def course_analytics(request: HttpRequest, course_id: int) -> HttpResponse:
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)

    # Get all lessons in this course through the modules
    course_lessons = Lesson.objects.filter(module__course=course)
    completed_count = CompletedLesson.objects.filter(lesson__in=course_lessons).count()

    context = {
        "course": course,
        "enrollments": course.enrollments.count(),  # type: ignore[attr-defined]
        "completed_lessons": completed_count,
    }
    return render(request, "teacher_dash/course_analytics.html", context)


@teacher_required
@onboarding_complete_required
def verification_status(request: HttpRequest) -> HttpResponse:
    teacher = _get_logged_in_teacher(request)
    profile = TeacherProfile.objects.filter(user=teacher).first()
    return render(request, "teacher_dash/verification_status.html", {"profile": profile})


@teacher_required
@onboarding_complete_required
def course_publish(request: HttpRequest, course_id: int) -> HttpResponse:
    if not _check_teacher_approval(request):
        return redirect("teacher_verification_status")
        
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)
    profile = TeacherProfile.objects.filter(user=teacher).first()

    if request.method == "POST":
        if profile and profile.verification_status == "approved":
            if course.admin_approved:
                # Admin has approved, teacher can now publish
                course.is_published = True
                course.is_submitted_for_review = False
                course.save(update_fields=["is_published", "is_submitted_for_review"])
                messages.success(request, "Course published and now visible to students.")
            else:
                # Admin hasn't approved yet, submit for review
                if not course.is_submitted_for_review:
                    course.is_submitted_for_review = True
                    course.admin_review_feedback = ""  # Clear old feedback when resubmitting
                    course.save(update_fields=["is_submitted_for_review", "admin_review_feedback"])
                    _notify_admins_course_submitted(course)
                    messages.info(request, "Course submitted for admin review. You can publish after approval.")
                else:
                    messages.info(request, "Awaiting admin review. You'll be able to publish after approval.")
        else:
            messages.error(request, "Your teacher profile must be approved to publish courses.")
    return redirect("teacher_course_detail", course_id=course.pk)


@teacher_required
@onboarding_complete_required
def course_unpublish(request: HttpRequest, course_id: int) -> HttpResponse:
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)
    if request.method == "POST":
        course.is_published = False
        course.save(update_fields=["is_published"])
        messages.success(request, "Course unpublished.")
    return redirect("teacher_course_detail", course_id=course.pk)


def _notify_admins_course_submitted(course: Course) -> None:
    try:
        mail_admins(
            subject="Course submitted for review",
            message=f"Course '{course.title}' requires approval.",
        )
    except Exception:
        pass


@teacher_required
@onboarding_complete_required
def export_courses(request: HttpRequest) -> HttpResponse:
    teacher = _get_logged_in_teacher(request)
    courses = Course.objects.filter(published_by=teacher)

    lines = ["title,price,is_published,id"]
    for course in courses:
        lines.append(f"{course.title},{course.price},{course.is_published},{course.pk}")

    response = HttpResponse("\n".join(lines), content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=teacher_courses.csv"
    return response


def serve_video(request: HttpRequest, video_path: str) -> FileResponse | HttpResponse:
    """Serve video files with HTTP Range request support for streaming"""
    import mimetypes

    # Build full file path
    file_path = os.path.join(settings.MEDIA_ROOT, video_path)

    # Security: Ensure file exists and is within MEDIA_ROOT
    real_media_root = os.path.realpath(settings.MEDIA_ROOT)
    real_file_path = os.path.realpath(file_path)

    if not os.path.exists(real_file_path) or not real_file_path.startswith(real_media_root):
        return HttpResponse("Video not found", status=404)

    # Get file size
    file_size = os.path.getsize(real_file_path)

    # Determine content type
    content_type, _ = mimetypes.guess_type(real_file_path)
    content_type = content_type or 'video/mp4'

    # Check for Range header
    range_header = request.META.get('HTTP_RANGE', '').strip()

    if range_header:
        # Parse range header (format: "bytes=start-end")
        range_match = range_header.replace('bytes=', '').split('-')
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if len(range_match) > 1 and range_match[1] else file_size - 1

        # Validate range
        if start >= file_size or end >= file_size or start > end:
            return HttpResponse("Invalid range", status=416)

        # Calculate content length
        length = end - start + 1

        # Open file and seek to start position
        file_handle = open(real_file_path, 'rb')
        file_handle.seek(start)

        # Create response with partial content
        response = FileResponse(file_handle, content_type=content_type, status=206)
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response['Content-Length'] = str(length)
        response['Accept-Ranges'] = 'bytes'

        return response
    else:
        # No range header - serve full file
        response = FileResponse(open(real_file_path, 'rb'), content_type=content_type)
        response['Content-Length'] = str(file_size)
        response['Accept-Ranges'] = 'bytes'

        return response


# ===== Discussion Board Views for Teachers =====

@teacher_required
@onboarding_complete_required
def course_discussions(request: HttpRequest, course_id: int) -> HttpResponse:
    """View and moderate course discussions"""
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)

    # Get sort parameter
    sort_param = request.GET.get('sort', 'recent')

    # Query top-level posts only (not replies)
    from django.core.paginator import Paginator
    posts_queryset = DiscussionPost.objects.filter(
        course=course,
        parent_post__isnull=True
    ).select_related('user').prefetch_related('replies')

    # Apply sorting
    if sort_param == 'pinned':
        posts_queryset = posts_queryset.order_by('-is_pinned', '-created_at')
    else:  # recent
        posts_queryset = posts_queryset.order_by('-created_at')

    # Pagination
    paginator = Paginator(posts_queryset, 20)
    page_number = request.GET.get('page', 1)
    posts_page = paginator.get_page(page_number)

    context = {
        'course': course,
        'posts': posts_page,
        'user_role': 'teacher',
        'sort': sort_param,
        'paginator': paginator,
    }
    return render(request, 'teacher_dash/course_discussions.html', context)


@teacher_required
@onboarding_complete_required
def discussion_create(request: HttpRequest, course_id: int) -> HttpResponse:
    """Create a new discussion post as teacher"""
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)

    if request.method == 'POST':
        form = DiscussionPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.course = course
            post.user = teacher
            post.parent_post = None  # Top-level post
            post.save()
            messages.success(request, "Your discussion post has been created!")
            return redirect('teacher_discussion_detail', course_id=course_id, post_id=post.id)
    else:
        form = DiscussionPostForm()

    context = {
        'course': course,
        'form': form,
        'action': 'create',
    }
    return render(request, 'teacher_dash/discussion_form.html', context)


@teacher_required
@onboarding_complete_required
def discussion_detail(request: HttpRequest, course_id: int, post_id: int) -> HttpResponse:
    """View a single discussion post with all replies"""
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)

    post = get_object_or_404(
        DiscussionPost.objects.select_related('user', 'course').prefetch_related('replies__user'),
        id=post_id,
        course=course
    )

    # Get all replies
    replies = post.get_replies()

    # Reply form
    reply_form = DiscussionReplyForm()

    context = {
        'course': course,
        'post': post,
        'replies': replies,
        'reply_form': reply_form,
        'user_role': 'teacher',
        'current_user': teacher,
    }
    return render(request, 'teacher_dash/discussion_detail.html', context)


@teacher_required
@onboarding_complete_required
def discussion_reply(request: HttpRequest, course_id: int, post_id: int) -> HttpResponse:
    """Reply to a discussion post"""
    if request.method != 'POST':
        return redirect('teacher_discussion_detail', course_id=course_id, post_id=post_id)

    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)
    parent_post = get_object_or_404(DiscussionPost, id=post_id, course=course)

    form = DiscussionReplyForm(request.POST)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.course = course
        reply.user = teacher
        reply.parent_post = parent_post
        reply.save()
        messages.success(request, "Your reply has been posted!")
    else:
        for error in form.errors.values():
            messages.error(request, str(error))

    return redirect('teacher_discussion_detail', course_id=course_id, post_id=post_id)


@teacher_required
@onboarding_complete_required
def discussion_edit(request: HttpRequest, course_id: int, post_id: int) -> HttpResponse:
    """Edit a discussion post or reply"""
    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)
    post = get_object_or_404(DiscussionPost, id=post_id, course=course)

    # Check if user can edit
    if not post.can_edit(teacher):
        messages.error(request, "You don't have permission to edit this post.")
        if post.parent_post:
            return redirect('teacher_discussion_detail', course_id=course_id, post_id=post.parent_post.id)
        return redirect('teacher_discussion_detail', course_id=course_id, post_id=post_id)

    if request.method == 'POST':
        form = DiscussionPostForm(request.POST, instance=post)
        if form.is_valid():
            from django.utils import timezone
            edited_post = form.save(commit=False)
            edited_post.is_edited = True
            edited_post.edited_at = timezone.now()
            edited_post.save()
            messages.success(request, "Post has been updated!")
            if post.parent_post:
                return redirect('teacher_discussion_detail', course_id=course_id, post_id=post.parent_post.id)
            return redirect('teacher_discussion_detail', course_id=course_id, post_id=post_id)
    else:
        form = DiscussionPostForm(instance=post)

    context = {
        'course': course,
        'form': form,
        'post': post,
        'action': 'edit',
    }
    return render(request, 'teacher_dash/discussion_form.html', context)


@teacher_required
@onboarding_complete_required
def discussion_delete(request: HttpRequest, course_id: int, post_id: int) -> HttpResponse:
    """Delete a discussion post or reply (teacher moderation)"""
    if request.method != 'POST':
        return redirect('teacher_course_discussions', course_id=course_id)

    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)
    post = get_object_or_404(DiscussionPost, id=post_id, course=course)

    # Teachers can delete any post in their course
    was_reply = post.parent_post is not None
    parent_id = post.parent_post.id if was_reply else None

    # Delete the post (replies will cascade)
    post.delete()
    messages.success(request, "Post deleted successfully.")

    # Redirect appropriately
    if was_reply and parent_id:
        return redirect('teacher_discussion_detail', course_id=course_id, post_id=parent_id)
    return redirect('teacher_course_discussions', course_id=course_id)


@teacher_required
@onboarding_complete_required
def discussion_pin_toggle(request: HttpRequest, course_id: int, post_id: int) -> HttpResponse:
    """Pin or unpin a discussion post"""
    if request.method != 'POST':
        return redirect('teacher_course_discussions', course_id=course_id)

    teacher = _get_logged_in_teacher(request)
    course = get_object_or_404(Course, pk=course_id, published_by=teacher)
    post = get_object_or_404(DiscussionPost, id=post_id, course=course, parent_post__isnull=True)

    # Toggle pin status
    post.is_pinned = not post.is_pinned
    post.save(update_fields=['is_pinned'])

    if post.is_pinned:
        messages.success(request, "Post has been pinned!")
    else:
        messages.success(request, "Post has been unpinned!")

    return redirect('teacher_discussion_detail', course_id=course_id, post_id=post_id)