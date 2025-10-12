from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TeacherProfile, StudentProfile, Enrollment, Payment


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'onboarding_complete', 'is_staff']
    list_filter = ['role', 'onboarding_complete', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'auth0_id', 'profile_picture', 'onboarding_complete')
        }),
    )


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'verification_status', 'specialization', 'years_experience', 'created_at']
    list_filter = ['verification_status', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'specialization']
    readonly_fields = ['created_at', 'updated_at', 'verified_at']

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Professional Info', {
            'fields': ('bio', 'credentials', 'specialization', 'years_experience')
        }),
        ('Documents', {
            'fields': ('resume', 'certifications')
        }),
        ('Verification', {
            'fields': ('verification_status', 'verification_notes', 'verified_by', 'verified_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'relationship', 'created_at']
    list_filter = ['relationship', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'care_recipient_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'progress_percentage', 'enrolled_at', 'is_active']
    list_filter = ['is_active', 'enrolled_at']
    search_fields = ['user__email', 'course__title']
    readonly_fields = ['enrolled_at']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['paypal_order_id', 'user', 'course', 'amount', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['user__email', 'course__title', 'paypal_order_id', 'paypal_payment_id', 'payer_email']
    readonly_fields = ['created_at', 'updated_at', 'completed_at', 'paypal_response']
    
    fieldsets = (
        ('Transaction', {
            'fields': ('user', 'course', 'status')
        }),
        ('PayPal Details', {
            'fields': ('paypal_order_id', 'paypal_payment_id', 'payer_email', 'payer_name')
        }),
        ('Payment Info', {
            'fields': ('amount', 'currency')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at', 'updated_at')
        }),
        ('Response Data', {
            'fields': ('paypal_response',),
            'classes': ('collapse',)
        }),
    )