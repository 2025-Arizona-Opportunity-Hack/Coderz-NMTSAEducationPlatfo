"""
PayPal Service Module
Handles PayPal Orders API v2 integration for course payments
"""
import logging
from decimal import Decimal
from django.conf import settings
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest, OrdersGetRequest
from paypalhttp import HttpError

logger = logging.getLogger(__name__)


class PayPalClient:
    """Singleton PayPal client"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize PayPal environment and client"""
        client_id = settings.PAYPAL_CLIENT_ID
        client_secret = settings.PAYPAL_CLIENT_SECRET
        mode = settings.PAYPAL_MODE

        if not client_id or not client_secret:
            raise ValueError("PayPal credentials not configured in settings")

        # Select environment based on mode
        if mode == 'live':
            environment = LiveEnvironment(client_id=client_id, client_secret=client_secret)
        else:
            environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)

        self.client = PayPalHttpClient(environment)
        logger.info(f"PayPal client initialized in {mode} mode")

    def get_client(self):
        """Get the PayPal HTTP client"""
        return self.client


def get_paypal_client():
    """Get or create PayPal client instance"""
    try:
        return PayPalClient().get_client()
    except Exception as e:
        logger.error(f"Failed to initialize PayPal client: {str(e)}")
        raise


def create_order(course, user, return_url=None, cancel_url=None):
    """
    Create a PayPal order for a course purchase
    
    Args:
        course: Course model instance
        user: User model instance
        return_url: Optional return URL after payment
        cancel_url: Optional cancel URL
        
    Returns:
        dict: PayPal order response with order_id
        
    Raises:
        Exception: If order creation fails
    """
    try:
        client = get_paypal_client()
        
        # Build order request
        request = OrdersCreateRequest()
        request.prefer('return=representation')
        
        # Order body
        order_data = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": f"course_{course.id}",
                    "description": f"Enrollment in {course.title}",
                    "custom_id": f"user_{user.id}_course_{course.id}",
                    "amount": {
                        "currency_code": "USD",
                        "value": str(course.price)
                    }
                }
            ],
            "application_context": {
                "brand_name": "NMTSA Learning",
                "user_action": "PAY_NOW",
                "shipping_preference": "NO_SHIPPING"
            }
        }
        
        # Add return/cancel URLs if provided
        if return_url:
            order_data["application_context"]["return_url"] = return_url
        if cancel_url:
            order_data["application_context"]["cancel_url"] = cancel_url
        
        request.request_body(order_data)
        
        # Execute request
        response = client.execute(request)
        
        logger.info(f"PayPal order created: {response.result.id} for user {user.id} course {course.id}")
        
        return {
            'success': True,
            'order_id': response.result.id,
            'status': response.result.status,
            'links': response.result.links
        }
        
    except HttpError as e:
        error_msg = str(e)
        logger.error(f"PayPal order creation failed: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Unexpected error creating PayPal order: {error_msg}")
        return {
            'success': False,
            'error': f"Payment system error: {error_msg}"
        }


def capture_order(order_id):
    """
    Capture a PayPal order (complete the payment)
    
    Args:
        order_id: PayPal order ID
        
    Returns:
        dict: Capture result with payment details
        
    Raises:
        Exception: If capture fails
    """
    try:
        client = get_paypal_client()
        
        request = OrdersCaptureRequest(order_id)
        response = client.execute(request)
        
        result = response.result
        
        # Extract payment details
        capture_data = {
            'success': True,
            'order_id': result.id,
            'status': result.status,
            'payer_email': None,
            'payer_name': None,
            'payment_id': None,
            'amount': None,
            'currency': 'USD'
        }
        
        # Extract payer information
        if hasattr(result, 'payer') and result.payer:
            payer = result.payer
            if hasattr(payer, 'email_address'):
                capture_data['payer_email'] = payer.email_address
            if hasattr(payer, 'name') and payer.name:
                name_parts = []
                if hasattr(payer.name, 'given_name'):
                    name_parts.append(payer.name.given_name)
                if hasattr(payer.name, 'surname'):
                    name_parts.append(payer.name.surname)
                capture_data['payer_name'] = ' '.join(name_parts)
        
        # Extract payment information
        if hasattr(result, 'purchase_units') and result.purchase_units:
            purchase_unit = result.purchase_units[0]
            
            # Get amount
            if hasattr(purchase_unit, 'amount'):
                capture_data['amount'] = Decimal(purchase_unit.amount.value)
                capture_data['currency'] = purchase_unit.amount.currency_code
            
            # Get capture/payment ID
            if hasattr(purchase_unit, 'payments') and purchase_unit.payments:
                if hasattr(purchase_unit.payments, 'captures') and purchase_unit.payments.captures:
                    capture = purchase_unit.payments.captures[0]
                    capture_data['payment_id'] = capture.id
        
        logger.info(f"PayPal order captured: {order_id} - Status: {result.status}")
        
        return capture_data
        
    except HttpError as e:
        error_msg = str(e)
        logger.error(f"PayPal order capture failed for {order_id}: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Unexpected error capturing PayPal order {order_id}: {error_msg}")
        return {
            'success': False,
            'error': f"Payment capture error: {error_msg}"
        }


def get_order_details(order_id):
    """
    Get details of a PayPal order
    
    Args:
        order_id: PayPal order ID
        
    Returns:
        dict: Order details
    """
    try:
        client = get_paypal_client()
        
        request = OrdersGetRequest(order_id)
        response = client.execute(request)
        
        result = response.result
        
        logger.info(f"Retrieved PayPal order details: {order_id}")
        
        return {
            'success': True,
            'order_id': result.id,
            'status': result.status,
            'result': result
        }
        
    except HttpError as e:
        error_msg = str(e)
        logger.error(f"Failed to get PayPal order details for {order_id}: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Unexpected error getting PayPal order details {order_id}: {error_msg}")
        return {
            'success': False,
            'error': f"Order retrieval error: {error_msg}"
        }
