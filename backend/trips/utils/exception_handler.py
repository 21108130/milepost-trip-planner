import logging

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):

    response = drf_exception_handler(exc, context)

    if response is not None:
        response.data = {
            "error": {
                "message": "Request failed.",
                "detail": response.data,
            }
        }
        return response

    
    logger.exception("Unhandled exception in view: %s", exc)
    return Response(
        {
            "error": {
                "message": "An unexpected server error occurred.",
                "detail": str(exc),
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
