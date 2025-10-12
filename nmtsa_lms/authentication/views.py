from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .models import User, TeacherProfile, StudentProfile
from .decorators import login_required, student_required, teacher_required, admin_required
from .forms import TeacherOnboardingForm, TeacherProfileForm, StudentOnboardingForm, StudentProfileForm
from django.views.decorators.http import require_http_methods
from django.core.files.storage import FileSystemStorage
import json
import uuid

def select_role(request):
    """
    First step of onboarding: user selects their role
    """
    if request.method == 'POST':
        role = request.POST.get('role')

        if role not in ['student', 'teacher']:
            messages.error(request, 'Please select a valid role.')
            return render(request, 'authentication/select_role.html')

        session_user = request.session.get('user')
        if not session_user:
            messages.error(request, 'Session expired. Please log in again.')
            return redirect('login')

        auth0_id = session_user.get('userinfo', {}).get('sub')
        email = session_user.get('userinfo', {}).get('email')
        name = session_user.get('userinfo', {}).get('name', '')
        picture = session_user.get('userinfo', {}).get('picture')

        name_parts = name.split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        try:
            user = User.objects.get(auth0_id=auth0_id)
        except User.DoesNotExist:
            username = email.split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                auth0_id=auth0_id,
                profile_picture=picture,
            )

        user.role = role
        user.save()

        request.session['user']['role'] = role
        request.session['user']['user_id'] = user.id
        request.session.modified = True

        if role == 'teacher':
            return redirect('teacher_onboarding')
        else:
            return redirect('student_onboarding')

    return render(request, 'authentication/select_role.html')


@login_required
def teacher_onboarding(request):
    """
    Teacher onboarding: collect credentials, resume, certifications
    """
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please log in again.')
        return redirect('login')

    teacher_profile, created = TeacherProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = TeacherOnboardingForm(request.POST, request.FILES, instance=teacher_profile)
        if form.is_valid():
            # Handle file renaming for security
            if 'resume' in request.FILES:
                request.FILES['resume'].name = f"{uuid.uuid4()}_{request.FILES['resume'].name}"
            if 'certifications' in request.FILES:
                request.FILES['certifications'].name = f"{uuid.uuid4()}_{request.FILES['certifications'].name}"
            
            teacher_profile = form.save()
            
            user.onboarding_complete = True
            user.save()

            request.session['user']['onboarding_complete'] = True
            request.session['user']['verification_status'] = 'pending'
            request.session.modified = True

            messages.success(request, 'Profile submitted successfully! Your application is pending admin verification.')
            
            # Check if there's a stored next URL to redirect to after onboarding
            next_url = request.session.pop('next_url', None)
            if next_url:
                return redirect(next_url)
            
            return redirect('teacher_dashboard')
    else:
        form = TeacherOnboardingForm(instance=teacher_profile)

    context = {
        'form': form,
        'teacher_profile': teacher_profile,
    }
    return render(request, 'authentication/teacher_onboarding.html', context)


@login_required
def student_onboarding(request):
    """
    Student onboarding: collect information about care recipient and needs
    """
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please log in again.')
        return redirect('login')

    student_profile, created = StudentProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = StudentOnboardingForm(request.POST, instance=student_profile)
        if form.is_valid():
            student_profile = form.save()
            
            user.onboarding_complete = True
            user.save()

            request.session['user']['onboarding_complete'] = True
            request.session.modified = True

            messages.success(request, 'Profile completed successfully! Welcome to NMTSA Learning.')
            
            # Check if there's a stored next URL to redirect to after onboarding
            next_url = request.session.pop('next_url', None)
            if next_url:
                return redirect(next_url)
            
            return redirect('student_dashboard')
    else:
        form = StudentOnboardingForm(instance=student_profile)

    context = {
        'form': form,
        'student_profile': student_profile,
        'relationship_choices': StudentProfile.RELATIONSHIP_CHOICES,
    }
    return render(request, 'authentication/student_onboarding.html', context)


@login_required
def profile_settings(request):
    """
    General profile settings page for all users
    """
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please log in again.')
        return redirect('login')

    teacher_form = None
    student_form = None

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()

        if user.is_teacher and hasattr(user, 'teacher_profile'):
            teacher_form = TeacherProfileForm(request.POST, instance=user.teacher_profile)
            if teacher_form.is_valid():
                teacher_form.save()

        elif user.is_student and hasattr(user, 'student_profile'):
            student_form = StudentProfileForm(request.POST, instance=user.student_profile)
            if student_form.is_valid():
                student_form.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile_settings')

    context = {
        'user': user,
    }

    if user.is_teacher and hasattr(user, 'teacher_profile'):
        context['teacher_profile'] = user.teacher_profile
        context['teacher_form'] = TeacherProfileForm(instance=user.teacher_profile)
    elif user.is_student and hasattr(user, 'student_profile'):
        context['student_profile'] = user.student_profile
        context['student_form'] = StudentProfileForm(instance=user.student_profile)
        context['relationship_choices'] = StudentProfile.RELATIONSHIP_CHOICES

    return render(request, 'authentication/profile_settings.html', context)
