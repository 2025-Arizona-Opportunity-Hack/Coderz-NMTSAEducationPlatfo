from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .models import User, TeacherProfile, StudentProfile
from .decorators import login_required, student_required, teacher_required, admin_required
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
        teacher_profile.bio = request.POST.get('bio', '')
        teacher_profile.credentials = request.POST.get('credentials', '')
        teacher_profile.specialization = request.POST.get('specialization', '')

        years_exp = request.POST.get('years_experience', '')
        if years_exp:
            try:
                teacher_profile.years_experience = int(years_exp)
            except ValueError:
                pass

        if 'resume' in request.FILES:
            teacher_profile.resume = request.FILES['resume']
            request.FILES['resume'].name = f"{uuid.uuid4()}_{request.FILES['resume'].name}"

        if 'certifications' in request.FILES:
            teacher_profile.certifications = request.FILES['certifications']
            request.FILES['certifications'].name = f"{uuid.uuid4()}_{request.FILES['certifications'].name}"

        teacher_profile.save()

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

    context = {
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
        student_profile.relationship = request.POST.get('relationship', '')
        student_profile.care_recipient_name = request.POST.get('care_recipient_name', '')

        care_age = request.POST.get('care_recipient_age', '')
        if care_age:
            try:
                student_profile.care_recipient_age = int(care_age)
            except ValueError:
                pass

        student_profile.special_needs = request.POST.get('special_needs', '')
        student_profile.learning_goals = request.POST.get('learning_goals', '')
        student_profile.interests = request.POST.get('interests', '')
        student_profile.accessibility_needs = request.POST.get('accessibility_needs', '')

        student_profile.save()

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

    context = {
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

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()

        if user.is_teacher and hasattr(user, 'teacher_profile'):
            profile = user.teacher_profile
            profile.bio = request.POST.get('bio', '')
            profile.specialization = request.POST.get('specialization', '')

            years_exp = request.POST.get('years_experience', '')
            if years_exp:
                try:
                    profile.years_experience = int(years_exp)
                except ValueError:
                    pass

            profile.save()

        elif user.is_student and hasattr(user, 'student_profile'):
            profile = user.student_profile
            profile.relationship = request.POST.get('relationship', '')
            profile.learning_goals = request.POST.get('learning_goals', '')
            profile.interests = request.POST.get('interests', '')
            profile.accessibility_needs = request.POST.get('accessibility_needs', '')
            profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile_settings')

    context = {
        'user': user,
    }

    if user.is_teacher and hasattr(user, 'teacher_profile'):
        context['teacher_profile'] = user.teacher_profile
    elif user.is_student and hasattr(user, 'student_profile'):
        context['student_profile'] = user.student_profile
        context['relationship_choices'] = StudentProfile.RELATIONSHIP_CHOICES

    return render(request, 'authentication/profile_settings.html', context)
