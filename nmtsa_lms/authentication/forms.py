from django import forms
from .models import TeacherProfile, StudentProfile


class TeacherOnboardingForm(forms.ModelForm):
    """Form for teacher onboarding"""
    
    class Meta:
        model = TeacherProfile
        fields = ['bio', 'credentials', 'specialization', 'years_experience', 'resume', 'certifications']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell us about your professional background and expertise...'
            }),
            'credentials': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'List your degrees, certifications, and qualifications...'
            }),
            'specialization': forms.TextInput(attrs={
                'placeholder': 'e.g., Neurologic Music Therapy, Autism Support, Music Education'
            }),
            'years_experience': forms.NumberInput(attrs={
                'min': 0,
                'max': 70,
                'placeholder': '5'
            }),
        }


class TeacherProfileForm(forms.ModelForm):
    """Form for editing teacher profile in settings"""
    
    class Meta:
        model = TeacherProfile
        fields = ['bio', 'specialization', 'years_experience']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell us about your professional background and expertise...'
            }),
        }


class StudentOnboardingForm(forms.ModelForm):
    """Form for student onboarding"""
    
    class Meta:
        model = StudentProfile
        fields = [
            'relationship', 
            'care_recipient_name', 
            'care_recipient_age',
            'special_needs', 
            'learning_goals', 
            'interests', 
            'accessibility_needs'
        ]
        widgets = {
            'special_needs': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe any special needs or conditions...'
            }),
            'learning_goals': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'What do you hope to learn or achieve?'
            }),
            'interests': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'What topics or areas interest you?'
            }),
            'accessibility_needs': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Any accessibility requirements?'
            }),
            'care_recipient_age': forms.NumberInput(attrs={
                'min': 0,
                'max': 120,
                'placeholder': 'Age in years'
            }),
        }


class StudentProfileForm(forms.ModelForm):
    """Form for editing student profile in settings"""
    
    class Meta:
        model = StudentProfile
        fields = ['relationship', 'learning_goals', 'interests', 'accessibility_needs']
        widgets = {
            'learning_goals': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'What do you hope to learn or achieve?'
            }),
            'interests': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'What topics or areas interest you?'
            }),
            'accessibility_needs': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Any accessibility requirements?'
            }),
        }
