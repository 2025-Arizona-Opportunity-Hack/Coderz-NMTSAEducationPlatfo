"""
Payment API views for PayPal integration
Handles course payment processing
"""

import requests
import base64
from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from authentication.models import Payment, Enrollment
from authentication.permissions import IsStudent, IsOnboardingComplete
from teacher_dash.models import Course


class PayPalConfig:
    """PayPal API configuration"""
    
    @staticmethod
    def get_access_token():
        """Get PayPal OAuth access token"""
        client_id = getattr(settings, 'PAYPAL_CLIENT_ID', '')
        client_secret = getattr(settings, 'PAYPAL_CLIENT_SECRET', '')
        base_url = getattr(settings, 'PAYPAL_BASE_URL', 'https://api-m.sandbox.paypal.com')
        
        if not client_id or not client_secret:
            raise ValueError("PayPal credentials not configured")
        
        auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers = {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(
            f'{base_url}/v1/oauth2/token',
            headers=headers,
            data={'grant_type': 'client_credentials'}
        )
        response.raise_for_status()
        return response.json()['access_token']
    
    @staticmethod
    def get_base_url():
        """Get PayPal API base URL"""
        return getattr(settings, 'PAYPAL_BASE_URL', 'https://api-m.sandbox.paypal.com')


class CreatePaymentOrderView(APIView):
    """
    POST /api/v1/student/payments/create-order/
    Creates a PayPal order for course payment
    """
    permission_classes = [IsAuthenticated, IsStudent, IsOnboardingComplete]
    
    def post(self, request):
        course_id = request.data.get('course_id')
        
        if not course_id:
            return Response(
                {'error': 'course_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get course and validate
        course = get_object_or_404(Course, id=course_id, is_published=True)
        
        if not course.is_paid:
            return Response(
                {'error': 'This course is not a paid course'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already enrolled
        if Enrollment.objects.filter(user=request.user, course=course).exists():
            return Response(
                {'error': 'You are already enrolled in this course'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if pending payment exists
        pending_payment = Payment.objects.filter(
            user=request.user,
            course=course,
            status='pending'
        ).first()
        
        if pending_payment:
            # Return existing order
            return Response({
                'order_id': pending_payment.paypal_order_id,
                'amount': str(pending_payment.amount),
                'currency': pending_payment.currency
            })
        
        try:
            # Get PayPal access token
            access_token = PayPalConfig.get_access_token()
            base_url = PayPalConfig.get_base_url()
            
            # Create PayPal order
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            
            order_data = {
                'intent': 'CAPTURE',
                'purchase_units': [{
                    'amount': {
                        'currency_code': 'USD',
                        'value': str(course.price)
                    },
                    'description': f'Enrollment for {course.title}',
                    'custom_id': f'course_{course.id}_user_{request.user.id}'
                }],
                'application_context': {
                    'brand_name': 'NMTSA Learn',
                    'landing_page': 'NO_PREFERENCE',
                    'user_action': 'PAY_NOW',
                    'return_url': f"{request.build_absolute_uri('/')[:-1]}/courses/{course.id}",
                    'cancel_url': f"{request.build_absolute_uri('/')[:-1]}/courses/{course.id}"
                }
            }
            
            response = requests.post(
                f'{base_url}/v2/checkout/orders',
                json=order_data,
                headers=headers
            )
            response.raise_for_status()
            order = response.json()
            
            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                course=course,
                paypal_order_id=order['id'],
                amount=course.price,
                currency='USD',
                status='pending'
            )
            
            return Response({
                'order_id': order['id'],
                'amount': str(course.price),
                'currency': 'USD'
            }, status=status.HTTP_201_CREATED)
            
        except requests.RequestException as e:
            return Response(
                {'error': f'PayPal API error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {'error': f'Error creating payment order: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CapturePaymentOrderView(APIView):
    """
    POST /api/v1/student/payments/capture-order/
    Captures a PayPal payment and enrolls user in course
    """
    permission_classes = [IsAuthenticated, IsStudent, IsOnboardingComplete]
    
    def post(self, request):
        order_id = request.data.get('order_id')
        
        if not order_id:
            return Response(
                {'error': 'order_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get payment record
        payment = get_object_or_404(Payment, paypal_order_id=order_id, user=request.user)
        
        if payment.status == 'completed':
            return Response(
                {'error': 'Payment already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get PayPal access token
            access_token = PayPalConfig.get_access_token()
            base_url = PayPalConfig.get_base_url()
            
            # Capture the payment
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.post(
                f'{base_url}/v2/checkout/orders/{order_id}/capture',
                headers=headers
            )
            response.raise_for_status()
            capture_data = response.json()
            
            # Check if capture was successful
            if capture_data.get('status') != 'COMPLETED':
                payment.mark_failed('Capture status not completed')
                return Response(
                    {'error': 'Payment capture failed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Extract payment details
            capture = capture_data['purchase_units'][0]['payments']['captures'][0]
            payer = capture_data.get('payer', {})
            
            # Mark payment as completed and enroll user
            with transaction.atomic():
                payment.mark_completed(
                    payment_id=capture['id'],
                    payer_info=payer,
                    response_data=capture_data
                )
                
                # Create enrollment
                enrollment, created = Enrollment.objects.get_or_create(
                    user=request.user,
                    course=payment.course,
                    defaults={'is_active': True}
                )
                
                if not created:
                    enrollment.is_active = True
                    enrollment.save()
                
                # Update course enrollment count
                payment.course.num_enrollments += 1
                payment.course.save(update_fields=['num_enrollments'])
            
            return Response({
                'success': True,
                'message': 'Payment completed successfully',
                'payment_id': capture['id'],
                'enrollment_id': enrollment.id
            }, status=status.HTTP_200_OK)
            
        except requests.RequestException as e:
            payment.mark_failed(str(e))
            return Response(
                {'error': f'PayPal API error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {'error': f'Error capturing payment: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentHistoryView(APIView):
    """
    GET /api/v1/student/payments/
    Returns user's payment history
    """
    permission_classes = [IsAuthenticated, IsStudent, IsOnboardingComplete]
    
    def get(self, request):
        payments = Payment.objects.filter(user=request.user).select_related('course')
        
        data = [{
            'id': payment.id,
            'course': {
                'id': payment.course.id,
                'title': payment.course.title
            },
            'amount': str(payment.amount),
            'currency': payment.currency,
            'status': payment.status,
            'paypal_order_id': payment.paypal_order_id,
            'created_at': payment.created_at.isoformat(),
            'completed_at': payment.completed_at.isoformat() if payment.completed_at else None
        } for payment in payments]
        
        return Response({'data': data}, status=status.HTTP_200_OK)
