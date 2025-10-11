from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from authentication.decorators import admin_required
from authentication.models import User, TeacherProfile
from teacher_dash.models import Course


@admin_required
def dashboard(request):
    """Admin dashboard homepage"""
    pending_teachers = TeacherProfile.objects.filter(verification_status='pending').count()
    total_users = User.objects.count()
    total_teachers = User.objects.filter(role='teacher').count()
    total_students = User.objects.filter(role='student').count()

    # Get pending course reviews
    pending_courses = Course.objects.filter(
        is_submitted_for_review=True
    ).select_related('published_by').prefetch_related('modules').order_by('-published_date')[:5]  # Show latest 5
    pending_courses_count = Course.objects.filter(is_submitted_for_review=True).count()

    context = {
        'pending_teachers': pending_teachers,
        'total_users': total_users,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'pending_courses': pending_courses,
        'pending_courses_count': pending_courses_count,
    }
    return render(request, 'admin_dash/dashboard.html', context)


@admin_required
def verify_teachers(request):
    """List of pending teacher verifications"""
    pending_teachers = TeacherProfile.objects.filter(
        verification_status='pending'
    ).select_related('user').order_by('-created_at')

    context = {
        'pending_teachers': pending_teachers,
    }
    return render(request, 'admin_dash/verify_teachers.html', context)


@admin_required
def verify_teacher_action(request, teacher_id):
    """Approve or reject a teacher application"""
    teacher_profile = get_object_or_404(TeacherProfile, id=teacher_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')

        session_user = request.session.get('user')
        admin_user_id = session_user.get('user_id')
        admin_user = User.objects.get(id=admin_user_id)

        if action == 'approve':
            teacher_profile.verification_status = 'approved'
            teacher_profile.verified_at = timezone.now()
            teacher_profile.verified_by = admin_user
            teacher_profile.verification_notes = notes
            teacher_profile.save()

            messages.success(request, f'Teacher {teacher_profile.user.get_full_name()} has been approved!')

        elif action == 'reject':
            teacher_profile.verification_status = 'rejected'
            teacher_profile.verification_notes = notes
            teacher_profile.save()

            messages.warning(request, f'Teacher {teacher_profile.user.get_full_name()} has been rejected.')

        return redirect('admin_verify_teachers')

    # GET request - show teacher details
    context = {
        'teacher_profile': teacher_profile,
    }
    return render(request, 'admin_dash/verify_teacher_detail.html', context)


@admin_required
def review_courses(request):
    courses = Course.objects.filter(is_submitted_for_review=True).select_related('published_by')
    return render(request, 'admin_dash/review_courses.html', {'courses': courses})


@admin_required
def review_course_action(request, course_id):
    """Approve or reject a course submission with optional feedback"""
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        feedback = request.POST.get('feedback', '').strip()

        if action == 'approve':
            course.is_published = True
            course.is_submitted_for_review = False
            course.admin_review_feedback = feedback
            course.save(update_fields=['is_published', 'is_submitted_for_review', 'admin_review_feedback'])
            messages.success(request, f"Approved course '{course.title}'.")
        elif action == 'reject':
            course.is_published = False
            course.is_submitted_for_review = False
            course.admin_review_feedback = feedback
            course.save(update_fields=['is_published', 'is_submitted_for_review', 'admin_review_feedback'])
            messages.info(request, f"Sent course '{course.title}' back to draft.")
        return redirect('admin_review_courses')

    # GET request - show review page with course details
    modules = course.modules.prefetch_related('lessons')
    total_lessons = sum([module.lessons.count() for module in modules])

    context = {
        'course': course,
        'modules': modules,
        'total_lessons': total_lessons,
    }
    return render(request, 'admin_dash/review_course_detail.html', context)


@admin_required
def admin_course_preview(request, course_id):
    """Preview course content (reuses teacher preview template)"""
    # Admins can preview any course, not just submitted ones
    course = get_object_or_404(Course, pk=course_id)

    # Same context structure as teacher preview
    modules = course.modules.prefetch_related("lessons", "lessons__video", "lessons__blog")

    context = {
        "course": course,
        "modules": modules,
        "is_admin_view": True,  # Flag for template customization if needed
    }

    # Reuse teacher preview template to avoid code duplication
    return render(request, "teacher_dash/course_preview.html", context)
