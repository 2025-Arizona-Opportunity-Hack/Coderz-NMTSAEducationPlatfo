"""
Custom exception handler for Django REST Framework
Provides consistent error response format across all API endpoints
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error responses

    Returns error responses in the format:
    {
        "error": "ErrorClassName",
        "message": "Human-readable error message",
        "status_code": 400,
        "details": {...}  # Optional field-level errors
    }
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the response format
        custom_response = {
            'error': exc.__class__.__name__,
            'message': str(exc),
            'status_code': response.status_code,
        }

        # Add detailed field errors if available
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                custom_response['details'] = exc.detail
            elif isinstance(exc.detail, list):
                custom_response['details'] = {'non_field_errors': exc.detail}

        return Response(custom_response, status=response.status_code)

    # If DRF's exception handler didn't handle it, return None
    # Django will handle it with a 500 error
    return response
