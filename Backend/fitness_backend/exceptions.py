"""
Custom DRF exception handler that catches ALL exceptions and returns
proper JSON responses with appropriate HTTP status codes.

Ported from NGU Backend — prevents Django from returning raw HTML 500 pages
for unhandled errors like model ValidationError, ValueError, TypeError, etc.
"""

import logging
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler:
    1. First tries DRF's default handler (handles APIException, Http404, PermissionDenied)
    2. Then catches Django model ValidationError → 400
    3. Then catches ValueError/TypeError → 400
    4. Finally catches everything else → 500 (with logging)
    """
    response = drf_exception_handler(exc, context)

    if response is not None:
        response.data = _normalize_error(response.data, response.status_code)
        return response

    # Django model ValidationError
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            errors = exc.message_dict
        elif hasattr(exc, 'messages'):
            errors = exc.messages
        else:
            errors = [str(exc)]

        logger.warning("Validation error in %s: %s", _get_view_name(context), errors)
        return Response(
            {'success': False, 'error': 'Validation error', 'details': errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ValueError / TypeError
    if isinstance(exc, (ValueError, TypeError)):
        logger.warning("Bad request data in %s: %s", _get_view_name(context), str(exc))
        return Response(
            {'success': False, 'error': f'Invalid input: {str(exc)}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # KeyError
    if isinstance(exc, KeyError):
        logger.warning("Missing key in %s: %s", _get_view_name(context), str(exc))
        return Response(
            {'success': False, 'error': f'Missing required field: {str(exc)}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # AttributeError
    if isinstance(exc, AttributeError):
        logger.error("AttributeError in %s: %s", _get_view_name(context), str(exc), exc_info=True)
        return Response(
            {'success': False, 'error': 'An internal error occurred. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Everything else
    logger.error("Unhandled exception in %s: %s", _get_view_name(context), str(exc), exc_info=True)
    return Response(
        {'success': False, 'error': 'An unexpected error occurred. Please try again later.'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _get_view_name(context):
    """Extract a human-readable view name from the exception context."""
    view = context.get('view')
    if view:
        cls = view.__class__
        return f"{cls.__module__}.{cls.__qualname__}"
    return 'unknown_view'


def _normalize_error(data, status_code):
    """Normalize DRF's default error format into a consistent shape."""
    if isinstance(data, dict):
        if 'detail' in data and len(data) == 1:
            return {'success': False, 'error': str(data['detail'])}
        if 'success' in data:
            return data
        return {'success': False, 'error': 'Validation error', 'details': data}
    if isinstance(data, list):
        return {'success': False, 'error': '; '.join(str(e) for e in data)}
    return {'success': False, 'error': str(data)}
