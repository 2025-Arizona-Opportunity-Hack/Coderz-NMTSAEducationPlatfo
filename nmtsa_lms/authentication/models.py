from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field

class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser
    Adds role field and Auth0 integration
    """
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        null=True,
        blank=True,
        help_text="User role in the system"
    )
    auth0_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text="Auth0 user ID"
    )
    profile_picture = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text="URL to user's profile picture from OAuth provider"
    )
    onboarding_complete = models.BooleanField(
        default=False,
        help_text="Whether user has completed onboarding"
    )

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})" if self.role else self.email

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_admin_user(self):
        return self.role == 'admin'


class TeacherProfile(models.Model):
    """
    Extended profile information for teachers
    Includes credentials, certifications, and verification status
    """
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    bio = CKEditor5Field('Bio', config_name='extends', blank=True)
    credentials = CKEditor5Field('Credentials', config_name='extends', blank=True)
    resume = models.FileField(
        upload_to='teacher_resumes/',
        null=True,
        blank=True,
        help_text="Resume/CV file"
    )
    certifications = models.FileField(
        upload_to='teacher_certifications/',
        null=True,
        blank=True,
        help_text="Certification documents"
    )
    verification_status = models.CharField(
        max_length=10,
        choices=VERIFICATION_STATUS,
        default='pending',
        help_text="Admin verification status"
    )
    verification_notes = CKEditor5Field('Verification Notes', config_name='extends', blank=True)
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when verified by admin"
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_teachers',
        help_text="Admin who verified this teacher"
    )
    specialization = models.CharField(
        max_length=200,
        blank=True,
        help_text="Area of specialization (e.g., Neurologic Music Therapy)"
    )
    years_experience = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Years of professional experience"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teacher_profiles'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_verification_status_display()}"

    @property
    def is_verified(self):
        return self.verification_status == 'approved'

    @property
    def is_pending(self):
        return self.verification_status == 'pending'


class StudentProfile(models.Model):
    """
    Extended profile information for students/families
    Includes information about care recipient and special needs
    """
    RELATIONSHIP_CHOICES = [
        ('parent', 'Parent'),
        ('guardian', 'Guardian'),
        ('caregiver', 'Professional Caregiver'),
        ('family', 'Family Member'),
        ('self', 'Self'),
        ('professional', 'Healthcare Professional'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        blank=True,
        help_text="Relationship to care recipient"
    )
    care_recipient_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name of person receiving care (optional)"
    )
    care_recipient_age = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Age of care recipient"
    )
    special_needs = CKEditor5Field('Special Needs', config_name='basic', blank=True)
    learning_goals = CKEditor5Field('Learning Goals', config_name='basic', blank=True)
    interests = CKEditor5Field('Interests', config_name='basic', blank=True)
    accessibility_needs = CKEditor5Field('Accessibility Needs', config_name='basic', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_profiles'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_relationship_display()}"


class Enrollment(models.Model):
    """
    Tracks student enrollment in courses
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        'teacher_dash.Course',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'enrollments'
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.email} enrolled in {self.course.title}"

    @property
    def is_completed(self):
        return self.completed_at is not None
    

class Payment(models.Model):
    """
    Tracks PayPal payment transactions for course purchases
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    # Relations
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    course = models.ForeignKey(
        'teacher_dash.Course',
        on_delete=models.CASCADE,
        related_name='payments'
    )

    # PayPal transaction details
    paypal_order_id = models.CharField(max_length=255, unique=True)
    paypal_payment_id = models.CharField(max_length=255, blank=True, null=True)
    payer_email = models.EmailField(blank=True, null=True)
    payer_name = models.CharField(max_length=255, blank=True, null=True)

    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Additional info
    paypal_response = models.JSONField(blank=True, null=True, help_text="Full PayPal API response")

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['course', '-created_at']),
            models.Index(fields=['paypal_order_id']),
        ]

    def __str__(self):
        return f"Payment {self.paypal_order_id} - {self.user.email} - {self.course.title}"

    @property
    def is_completed(self):
        return self.status == 'completed'

    def mark_completed(self, payment_id, payer_info=None, response_data=None):
        """Mark payment as completed and store PayPal details"""
        from django.utils import timezone

        self.status = 'completed'
        self.paypal_payment_id = payment_id
        self.completed_at = timezone.now()

        if payer_info:
            self.payer_email = payer_info.get('email_address')
            payer_name = payer_info.get('name', {})
            self.payer_name = f"{payer_name.get('given_name', '')} {payer_name.get('surname', '')}".strip()

        if response_data:
            self.paypal_response = response_data

        self.save()

    def mark_failed(self, reason=None):
        """Mark payment as failed"""
        self.status = 'failed'
        if reason and self.paypal_response:
            self.paypal_response['failure_reason'] = reason
        self.save()
