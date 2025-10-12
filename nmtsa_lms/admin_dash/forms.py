from django import forms


class CourseReviewForm(forms.Form):
    """Form for admin course review"""
    
    ACTION_CHOICES = [
        ('approve', 'Approve Course'),
        ('reject', 'Send Back for Revisions'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )
    
    feedback = forms.CharField(
        label='Feedback for Teacher',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': 'Provide optional feedback to the teacher...'
        })
    )


class TeacherVerificationForm(forms.Form):
    """Form for admin teacher verification"""
    
    ACTION_CHOICES = [
        ('approve', 'Approve Teacher'),
        ('reject', 'Reject Application'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )
    
    notes = forms.CharField(
        label='Admin Notes',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': 'Add any notes about this verification decision...'
        })
    )
