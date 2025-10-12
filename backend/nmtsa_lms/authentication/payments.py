"""
Payment models for tracking PayPal transactions
"""

from django.db import models
from django.conf import settings
from decimal import Decimal


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
