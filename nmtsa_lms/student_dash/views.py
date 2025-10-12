from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, F, Count
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from typing import Any, cast
import json
import logging
from authentication.decorators import student_required, onboarding_complete_required
from authentication.models import User, Enrollment, Payment
from teacher_dash.models import Course, Module, Lesson, VideoLesson, BlogLesson, DiscussionPost
from teacher_dash.forms import DiscussionPostForm, DiscussionReplyForm
from lms.models import CompletedLesson, VideoProgress
from django.core.paginator import Paginator
from nmtsa_lms.paypal_service import create_order as paypal_create_order, capture_order as paypal_capture_order

logger = logging.getLogger(__name__)


@student_required
@onboarding_complete_required
def dashboard(request):
    """Student dashboard homepage"""
    # Get session user
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    # Get enrolled courses
    enrollments = Enrollment.objects.filter(user=user, is_active=True).select_related('course', 'course__published_by')

    # Separate in-progress and completed courses
    in_progress_courses = enrollments.filter(completed_at__isnull=True, progress_percentage__lt=100).order_by('-enrolled_at')[:3]
    completed_count = enrollments.filter(completed_at__isnull=False).count()
    enrolled_count = enrollments.count()

    # Calculate total learning hours (estimate based on course duration)
    learning_hours = sum([e.progress_percentage * 0.1 for e in enrollments])  # Simplified calculation

    # Get recommended courses (published courses user is not enrolled in)
    enrolled_course_ids = enrollments.values_list('course_id', flat=True)
    recommended_courses = Course.objects.filter(
        is_published=True
    ).exclude(
        id__in=enrolled_course_ids
    ).order_by('-num_enrollments')[:6]

    context = {
        'enrolled_count': enrolled_count,
        'completed_count': completed_count,
        'learning_hours': int(learning_hours),
        'in_progress_courses': in_progress_courses,
        'recommended_courses': recommended_courses,
    }
    return render(request, 'student_dash/dashboard.html', context)


@student_required
@onboarding_complete_required
def courses(request):
    """Student's enrolled courses"""
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    # Get all enrollments
    enrollments = Enrollment.objects.filter(
        user=user,
        is_active=True
    ).select_related('course', 'course__published_by').order_by('-enrolled_at')

    context = {
        'enrollments': enrollments,
    }
    return render(request, 'student_dash/my_courses.html', context)


@student_required
@onboarding_complete_required
def catalog(request):
    """Course catalog for browsing"""
    # Base queryset
    qs = Course.objects.filter(is_published=True).select_related('published_by').prefetch_related('tags')

    # Filters from query params
    q = request.GET.get('q', '').strip()
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    tag = request.GET.get('tag', '').strip()
    sort = request.GET.get('sort', 'newest')

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

    if price_min:
        try:
            qs = qs.filter(price__gte=float(price_min))
        except ValueError:
            pass

    if price_max:
        try:
            qs = qs.filter(price__lte=float(price_max))
        except ValueError:
            pass

    if tag:
        qs = qs.filter(tags__name__iexact=tag)

    # Sorting
    if sort == 'popular':
        qs = qs.order_by('-num_enrollments', '-published_date')
    elif sort == 'price_asc':
        qs = qs.order_by('price')
    elif sort == 'price_desc':
        qs = qs.order_by('-price')
    else:  # newest
        qs = qs.order_by('-published_date')

    context = {
        'courses': qs,
        'filters': {
            'q': q,
            'price_min': price_min or '',
            'price_max': price_max or '',
            'tag': tag,
            'sort': sort,
        }
    }
    return render(request, 'student_dash/course_catalog.html', context)


@student_required
@onboarding_complete_required
def course_detail(request, course_id):
    """Course detail page with enrollment option"""
    course = get_object_or_404(Course, id=course_id, is_published=True)

    # Check if user is already enrolled
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    enrollment = Enrollment.objects.filter(user=user, course=course).first()

    # Get course modules and lessons
    modules = course.modules.all().prefetch_related('lessons')

    # Count total lessons
    total_lessons = sum([module.lessons.count() for module in modules])

    context = {
        'course': course,
        'enrollment': enrollment,
        'modules': modules,
        'total_lessons': total_lessons,
    }
    return render(request, 'student_dash/course_detail.html', context)


@student_required
@onboarding_complete_required
def enroll_in_course(request, course_id):
    """Enroll student in a course"""
    if request.method != 'POST':
        return redirect('student_catalog')

    course = get_object_or_404(Course, id=course_id, is_published=True)
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    # Redirect to checkout for paid courses
    if course.is_paid:
        return redirect('student_checkout', course_id=course_id)

    # Check if already enrolled
    existing_enrollment = Enrollment.objects.filter(user=user, course=course).first()

    if existing_enrollment:
        messages.warning(request, "You're already enrolled in this course!")
        return redirect('student_course_detail', course_id=course_id)

    # Create enrollment for free courses
    with transaction.atomic():
        Enrollment.objects.create(
            user=user,
            course=course,
            progress_percentage=0,
            is_active=True
        )
        # Update course enrollment count
        Course.objects.filter(pk=course.pk).update(num_enrollments=F('num_enrollments') + 1)

    messages.success(request, f"Successfully enrolled in {course.title}!")
    return redirect('student_course_detail', course_id=course_id)


@student_required
@onboarding_complete_required
def checkout_course(request, course_id):
    """Display checkout page for paid course"""
    course = get_object_or_404(Course, id=course_id, is_published=True)
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    # Check if not a paid course
    if not course.is_paid:
        messages.info(request, "This course is free! No payment required.")
        return redirect('student_enroll', course_id=course_id)

    # Check if already enrolled
    existing_enrollment = Enrollment.objects.filter(user=user, course=course).first()
    if existing_enrollment:
        messages.warning(request, "You're already enrolled in this course!")
        return redirect('student_course_detail', course_id=course_id)

    # Import settings to get PayPal client ID
    from django.conf import settings
    
    context = {
        'course': course,
        'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID,
    }
    return render(request, 'student_dash/checkout.html', context)


@student_required
@onboarding_complete_required
def process_checkout(request, course_id):
    """Process payment and create enrollment"""
    if request.method != 'POST':
        return redirect('student_checkout', course_id=course_id)

    course = get_object_or_404(Course, id=course_id, is_published=True)
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    # Check if already enrolled
    existing_enrollment = Enrollment.objects.filter(user=user, course=course).first()
    if existing_enrollment:
        messages.warning(request, "You're already enrolled in this course!")
        return redirect('student_course_detail', course_id=course_id)

    # Simulate payment processing
    # In production, this would integrate with Stripe/PayPal
    # For now, we just create the enrollment

    with transaction.atomic():
        # Create enrollment
        Enrollment.objects.create(
            user=user,
            course=course,
            progress_percentage=0,
            is_active=True
        )
        # Update course enrollment count
        Course.objects.filter(pk=course.pk).update(num_enrollments=F('num_enrollments') + 1)

    messages.success(request, f"Payment successful! You're now enrolled in {course.title}. Welcome aboard!")
    return redirect('student_learning', course_id=course_id)


@student_required
@onboarding_complete_required
@require_http_methods(["POST"])
def create_paypal_order(request, course_id):
    """
    API endpoint to create a PayPal order
    Called by frontend when user clicks PayPal button
    """
    try:
        session_user = request.session.get('user')
        user_id = session_user.get('user_id')
        user = User.objects.get(id=user_id)
        
        course = get_object_or_404(Course, id=course_id, is_published=True)
        
        # Verify course is paid
        if not course.is_paid:
            return JsonResponse({
                'success': False,
                'error': 'This course is free and does not require payment'
            }, status=400)
        
        # Check if already enrolled
        existing_enrollment = Enrollment.objects.filter(user=user, course=course).first()
        if existing_enrollment:
            return JsonResponse({
                'success': False,
                'error': 'You are already enrolled in this course'
            }, status=400)
        
        # Check for existing pending payment
        existing_payment = Payment.objects.filter(
            user=user,
            course=course,
            status='pending'
        ).first()
        
        if existing_payment:
            # Return existing order ID if payment still pending
            return JsonResponse({
                'success': True,
                'order_id': existing_payment.paypal_order_id
            })
        
        # Create PayPal order
        result = paypal_create_order(course, user)
        
        if not result.get('success'):
            logger.error(f"PayPal order creation failed: {result.get('error')}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to create payment order. Please try again.'
            }, status=500)
        
        # Store payment record
        payment = Payment.objects.create(
            user=user,
            course=course,
            paypal_order_id=result['order_id'],
            amount=course.price,
            currency='USD',
            status='pending'
        )
        
        logger.info(f"Payment record created: {payment.id} for order {result['order_id']}")
        
        return JsonResponse({
            'success': True,
            'order_id': result['order_id']
        })
        
    except Course.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Course not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error creating PayPal order: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }, status=500)


@student_required
@onboarding_complete_required
@require_http_methods(["POST"])
def capture_paypal_order(request, course_id):
    """
    API endpoint to capture a PayPal order after user approval
    Called by frontend after user completes payment in PayPal popup
    """
    try:
        # Parse request body
        data = json.loads(request.body)
        order_id = data.get('order_id')
        
        if not order_id:
            return JsonResponse({
                'success': False,
                'error': 'Order ID is required'
            }, status=400)
        
        session_user = request.session.get('user')
        user_id = session_user.get('user_id')
        user = User.objects.get(id=user_id)
        
        course = get_object_or_404(Course, id=course_id, is_published=True)
        
        # Get payment record
        payment = Payment.objects.filter(
            paypal_order_id=order_id,
            user=user,
            course=course
        ).first()
        
        if not payment:
            return JsonResponse({
                'success': False,
                'error': 'Payment record not found'
            }, status=404)
        
        # Check if already captured
        if payment.status == 'completed':
            # Check if enrollment exists
            enrollment = Enrollment.objects.filter(user=user, course=course).first()
            if enrollment:
                return JsonResponse({
                    'success': True,
                    'message': 'Payment already processed',
                    'redirect_url': f'/student/courses/{course_id}/learn/'
                })
        
        # Capture the PayPal order
        capture_result = paypal_capture_order(order_id)
        
        if not capture_result.get('success'):
            logger.error(f"PayPal capture failed for order {order_id}: {capture_result.get('error')}")
            payment.status = 'failed'
            payment.save()
            return JsonResponse({
                'success': False,
                'error': 'Payment capture failed. Please contact support.'
            }, status=500)
        
        # Use transaction to ensure atomicity
        with transaction.atomic():
            # Update payment record
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.paypal_payment_id = capture_result.get('payment_id', '')
            payment.payer_email = capture_result.get('payer_email', '')
            payment.payer_name = capture_result.get('payer_name', '')
            payment.save()
            
            # Create enrollment (check again to prevent race condition)
            enrollment, created = Enrollment.objects.get_or_create(
                user=user,
                course=course,
                defaults={
                    'progress_percentage': 0,
                    'is_active': True
                }
            )
            
            if created:
                # Update course enrollment count
                Course.objects.filter(pk=course.pk).update(num_enrollments=F('num_enrollments') + 1)
                logger.info(f"Enrollment created for user {user.id} in course {course.id} via PayPal payment {payment.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Payment successful! Welcome to the course.',
            'redirect_url': f'/student/courses/{course_id}/learn/'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid request data'
        }, status=400)
    except Course.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Course not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error capturing PayPal order: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }, status=500)


@student_required
@onboarding_complete_required
def learning(request, course_id):
    """Main learning interface for a course"""
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, user=user, course=course)

    # Get all modules with lessons
    modules = course.modules.all().prefetch_related('lessons')

    # Get first lesson of first module as default
    first_lesson = None
    first_module = None
    for module in modules:
        if module.lessons.exists():
            first_module = module
            first_lesson = module.lessons.first()
            break

    if not first_lesson or not first_module:
        messages.warning(request, "This course doesn't have any lessons yet.")
        return redirect('student_course_detail', course_id=course_id)

    # Redirect to the first lesson
    return redirect('student_lesson', course_id=course_id, module_id=first_module.id, lesson_id=first_lesson.id)


@student_required
@onboarding_complete_required
def lesson_view(request, course_id, module_id, lesson_id):
    """View a specific lesson"""
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, user=user, course=course)
    module = get_object_or_404(Module, id=module_id)
    current_lesson = get_object_or_404(Lesson, id=lesson_id)

    # Load video progress for video lessons
    video_progress = None
    if current_lesson.lesson_type == 'video':
        try:
            video_obj = VideoLesson.objects.get(lesson=current_lesson)
            video_progress = VideoProgress.objects.filter(
                enrollment=enrollment,
                lesson=current_lesson
            ).first()
        except VideoLesson.DoesNotExist:
            video_obj = None
        # Attach dynamically for template consumption
        cast(Any, current_lesson).video = video_obj
    elif current_lesson.lesson_type == 'blog':
        try:
            blog_obj = BlogLesson.objects.get(lesson=current_lesson)
        except BlogLesson.DoesNotExist:
            blog_obj = None
        cast(Any, current_lesson).blog = blog_obj

    # Get all modules for sidebar
    modules = course.modules.all().prefetch_related('lessons').order_by('id')

    # Completed lessons for this enrollment
    completed_lesson_ids = list(
        CompletedLesson.objects.filter(enrollment=enrollment).values_list('lesson_id', flat=True)
    )

    # Get video progress for all video lessons to show watch percentage
    video_progress_map = {}
    for vp in VideoProgress.objects.filter(enrollment=enrollment):
        video_progress_map[vp.lesson_id] = vp.completed_percentage

    # Find previous and next lessons
    all_lessons = []
    for mod in modules:
        for lesson in mod.lessons.all():
            lesson.module_id = mod.id
            # Add watch percentage for sidebar display
            if lesson.lesson_type == 'video':
                lesson.watch_percentage = video_progress_map.get(lesson.id, 0)
            all_lessons.append(lesson)

    current_index = next((i for i, l in enumerate(all_lessons) if l.id == lesson_id), None)
    previous_lesson = all_lessons[current_index - 1] if current_index and current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index is not None and current_index < len(all_lessons) - 1 else None

    context = {
        'course': course,
        'enrollment': enrollment,
        'module': module,
        'modules': modules,
        'current_lesson': current_lesson,
        'completed_lesson_ids': completed_lesson_ids,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
        'video_progress': video_progress,
    }
    return render(request, 'student_dash/learning.html', context)


@student_required
@onboarding_complete_required
def mark_lesson_complete(request, course_id, module_id, lesson_id):
    """Mark a lesson as complete and update progress"""
    if request.method != 'POST':
        return redirect('student_lesson', course_id=course_id, module_id=module_id, lesson_id=lesson_id)

    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, user=user, course=course)

    # Ensure the lesson exists
    lesson = get_object_or_404(Lesson, id=lesson_id)

    with transaction.atomic():
        # Create CompletedLesson if not exists (idempotent)
        CompletedLesson.objects.get_or_create(enrollment=enrollment, lesson=lesson)

        # Recompute progress deterministically
        modules = course.modules.all().prefetch_related('lessons')
        total_lessons = sum([m.lessons.count() for m in modules]) or 1

        completed_count = CompletedLesson.objects.filter(enrollment=enrollment).count()
        progress = int((completed_count / total_lessons) * 100)

        # Update enrollment progress and completion timestamp
        Enrollment.objects.filter(pk=enrollment.pk).update(
            progress_percentage=progress,
            completed_at=timezone.now() if progress >= 100 and not enrollment.completed_at else enrollment.completed_at,
        )

    messages.success(request, "Lesson marked as complete!")
    return redirect('student_lesson', course_id=course_id, module_id=module_id, lesson_id=lesson_id)


@student_required
@onboarding_complete_required
def certificate(request, course_id):
    """Display certificate for completed course"""
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, user=user, course=course, completed_at__isnull=False)

    context = {
        'course': course,
        'enrollment': enrollment,
    }
    return render(request, 'student_dash/certificate.html', context)


@student_required
@onboarding_complete_required
def certificate_pdf(request, course_id):
    """Optional PDF generation for certificate; falls back gracefully if dependency missing."""
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, user=user, course=course, completed_at__isnull=False)

    # Render HTML from the same template
    html_string = render_to_string('student_dash/certificate.html', {
        'course': course,
        'enrollment': enrollment,
    }, request=request)

    try:
        from weasyprint import HTML  # type: ignore
    except Exception:
        messages.info(request, "PDF generation is not available. Use your browser's Print to PDF.")
        return redirect('student_certificate', course_id=course_id)

    pdf_bytes = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    filename = f"certificate-{course.pk}-{enrollment.pk}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


@student_required
@require_http_methods(["POST"])
def save_video_progress(request):
    """API endpoint to save video playback progress"""
    try:
        data = json.loads(request.body)
        lesson_id = data.get('lesson_id')
        current_time = data.get('current_time', 0)
        duration = data.get('duration', 0)

        session_user = request.session.get('user')
        user_id = session_user.get('user_id')
        user = User.objects.get(id=user_id)

        lesson = get_object_or_404(Lesson, id=lesson_id)
        enrollment = get_object_or_404(
            Enrollment,
            user=user,
            course__modules__lessons=lesson
        )

        # Calculate completion percentage
        completed_percentage = 0
        if duration > 0:
            completed_percentage = min(int((current_time / duration) * 100), 100)

        # Update or create video progress
        video_progress, created = VideoProgress.objects.update_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={
                'last_position_seconds': int(current_time),
                'completed_percentage': completed_percentage
            }
        )

        return JsonResponse({
            'success': True,
            'progress': completed_percentage,
            'position': int(current_time)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# ===== Discussion Board Views =====

def _can_access_discussions(user, course):
    """Check if user can access course discussions"""
    # Admins can access all discussions
    if hasattr(user, 'is_admin_user') and user.is_admin_user:
        return True

    # Course teacher can access
    if course.published_by == user:
        return True

    # Students must be enrolled
    if hasattr(user, 'is_student') and user.is_student:
        enrollment = Enrollment.objects.filter(user=user, course=course, is_active=True).first()
        return enrollment is not None

    return False


def _get_user_role_in_course(user, course):
    """Get user's role in a specific course"""
    if hasattr(user, 'is_admin_user') and user.is_admin_user:
        return 'admin'

    if course.published_by == user:
        return 'teacher'

    if hasattr(user, 'is_student') and user.is_student:
        enrollment = Enrollment.objects.filter(user=user, course=course, is_active=True).first()
        if enrollment:
            return 'student'

    return None


@student_required
@onboarding_complete_required
def course_discussions(request, course_id):
    """List all discussion posts for a course"""
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    course = get_object_or_404(Course, id=course_id, is_published=True)

    # Check access
    if not _can_access_discussions(user, course):
        messages.error(request, "You must be enrolled in this course to view discussions.")
        return redirect('student_course_detail', course_id=course_id)

    # Get user's enrollment
    enrollment = get_object_or_404(Enrollment, user=user, course=course, is_active=True)

    # Get sort parameter
    sort = request.GET.get('sort', 'recent')

    # Query top-level posts only (not replies)
    posts_queryset = DiscussionPost.objects.filter(
        course=course,
        parent_post__isnull=True
    ).select_related('user').prefetch_related('replies')

    # Apply sorting
    if sort == 'unanswered':
        # Annotate with reply_count and filter unanswered
        posts_queryset = posts_queryset.annotate(reply_count=Count('replies')).filter(reply_count=0).order_by('-created_at')
    elif sort == 'pinned':
        posts_queryset = posts_queryset.order_by('-is_pinned', '-created_at')
    else:  # recent
        posts_queryset = posts_queryset.order_by('-created_at')

    # Pagination
    paginator = Paginator(posts_queryset, 20)
    page_number = request.GET.get('page', 1)
    posts_page = paginator.get_page(page_number)

    # Get user role for template
    user_role = _get_user_role_in_course(user, course)

    context = {
        'course': course,
        'enrollment': enrollment,
        'posts': posts_page,
        'user_role': user_role,
        'sort': sort,
        'paginator': paginator,
    }
    return render(request, 'student_dash/course_discussions.html', context)


@student_required
@onboarding_complete_required
def discussion_create(request, course_id):
    """Create a new discussion post"""
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    course = get_object_or_404(Course, id=course_id, is_published=True)

    # Check access
    if not _can_access_discussions(user, course):
        messages.error(request, "You must be enrolled in this course to post discussions.")
        return redirect('student_course_detail', course_id=course_id)

    # Rate limiting check - max 10 posts per hour per user per course
    from django.utils import timezone
    from datetime import timedelta
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_posts_count = DiscussionPost.objects.filter(
        course=course,
        user=user,
        created_at__gte=one_hour_ago
    ).count()

    if recent_posts_count >= 10:
        messages.error(request, "You've reached the posting limit. Please wait before posting again.")
        return redirect('student_course_discussions', course_id=course_id)

    if request.method == 'POST':
        form = DiscussionPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.course = course
            post.user = user
            post.parent_post = None  # Top-level post
            post.save()
            messages.success(request, "Your discussion post has been created!")
            return redirect('student_discussion_detail', course_id=course_id, post_id=post.id)
    else:
        form = DiscussionPostForm()

    context = {
        'course': course,
        'form': form,
        'action': 'create',
    }
    return render(request, 'student_dash/discussion_form.html', context)


@student_required
@onboarding_complete_required
def discussion_detail(request, course_id, post_id):
    """View a single discussion post with all replies"""
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    course = get_object_or_404(Course, id=course_id, is_published=True)

    # Check access
    if not _can_access_discussions(user, course):
        messages.error(request, "You must be enrolled in this course to view discussions.")
        return redirect('student_course_detail', course_id=course_id)

    post = get_object_or_404(
        DiscussionPost.objects.select_related('user', 'course').prefetch_related('replies__user'),
        id=post_id,
        course=course
    )

    # Get all replies
    replies = post.get_replies()

    # Get user role for template
    user_role = _get_user_role_in_course(user, course)

    # Reply form
    reply_form = DiscussionReplyForm()

    context = {
        'course': course,
        'post': post,
        'replies': replies,
        'reply_form': reply_form,
        'user_role': user_role,
        'current_user': user,
    }
    return render(request, 'student_dash/discussion_detail.html', context)


@student_required
@onboarding_complete_required
def discussion_reply(request, course_id, post_id):
    """Reply to a discussion post"""
    if request.method != 'POST':
        return redirect('student_discussion_detail', course_id=course_id, post_id=post_id)

    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    course = get_object_or_404(Course, id=course_id, is_published=True)

    # Check access
    if not _can_access_discussions(user, course):
        messages.error(request, "You must be enrolled in this course to reply.")
        return redirect('student_course_detail', course_id=course_id)

    parent_post = get_object_or_404(DiscussionPost, id=post_id, course=course)

    # Rate limiting
    from django.utils import timezone
    from datetime import timedelta
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_posts_count = DiscussionPost.objects.filter(
        course=course,
        user=user,
        created_at__gte=one_hour_ago
    ).count()

    if recent_posts_count >= 10:
        messages.error(request, "You've reached the posting limit. Please wait before replying again.")
        return redirect('student_discussion_detail', course_id=course_id, post_id=post_id)

    form = DiscussionReplyForm(request.POST)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.course = course
        reply.user = user
        reply.parent_post = parent_post
        reply.save()
        messages.success(request, "Your reply has been posted!")
    else:
        for field_errors in form.errors.values():
            for err in field_errors:
                messages.error(request, str(err))

    return redirect('student_discussion_detail', course_id=course_id, post_id=post_id)


@student_required
@onboarding_complete_required
def discussion_edit(request, course_id, post_id):
    """Edit a discussion post or reply"""
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    course = get_object_or_404(Course, id=course_id, is_published=True)
    post = get_object_or_404(DiscussionPost, id=post_id, course=course)

    # Check if user can edit
    if not post.can_edit(user):
        messages.error(request, "You don't have permission to edit this post, or the editing time limit has expired.")
        if post.parent_post:
            return redirect('student_discussion_detail', course_id=course_id, post_id=post.parent_post.id)
        return redirect('student_discussion_detail', course_id=course_id, post_id=post_id)

    if request.method == 'POST':
        form = DiscussionPostForm(request.POST, instance=post)
        if form.is_valid():
            edited_post = form.save(commit=False)
            edited_post.is_edited = True
            edited_post.edited_at = timezone.now()
            edited_post.save()
            messages.success(request, "Your post has been updated!")
            if post.parent_post:
                return redirect('student_discussion_detail', course_id=course_id, post_id=post.parent_post.id)
            return redirect('student_discussion_detail', course_id=course_id, post_id=post_id)
    else:
        form = DiscussionPostForm(instance=post)

    context = {
        'course': course,
        'form': form,
        'post': post,
        'action': 'edit',
    }
    return render(request, 'student_dash/discussion_form.html', context)


@student_required
@onboarding_complete_required
def discussion_delete(request, course_id, post_id):
    """Delete a discussion post or reply"""
    if request.method != 'POST':
        return redirect('student_course_discussions', course_id=course_id)

    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    course = get_object_or_404(Course, id=course_id, is_published=True)
    post = get_object_or_404(DiscussionPost, id=post_id, course=course)

    # Check if user can delete
    if not post.can_delete(user, course):
        messages.error(request, "You don't have permission to delete this post.")
        return redirect('student_course_discussions', course_id=course_id)

    # Remember if it was a reply
    was_reply = post.parent_post is not None
    parent_id = post.parent_post.id if was_reply and post.parent_post else None

    # Delete the post (replies will cascade)
    post.delete()
    messages.success(request, "Post deleted successfully.")

    # Redirect appropriately
    if was_reply and parent_id:
        return redirect('student_discussion_detail', course_id=course_id, post_id=parent_id)
    return redirect('student_course_discussions', course_id=course_id)