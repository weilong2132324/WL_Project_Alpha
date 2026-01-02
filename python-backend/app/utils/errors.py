"""Error handling and responses"""

import logging
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from app.schemas import StandardResponse

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception"""
    
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UnauthorizedException(AppException):
    """Unauthorized exception"""
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AppException):
    """Forbidden exception"""
    
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class NotFoundException(AppException):
    """Not found exception"""
    
    def __init__(self, message: str = "Not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class BadRequestException(AppException):
    """Bad request exception"""
    
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class ConflictException(AppException):
    """Conflict exception"""
    
    def __init__(self, message: str = "Conflict"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class InternalServerException(AppException):
    """Internal server error exception"""
    
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


def success_response(message: str = "Success", data=None, status_code: int = status.HTTP_200_OK):
    """Create a success response"""
    return JSONResponse(
        status_code=status_code,
        content=StandardResponse(
            success=True,
            message=message,
            data=data
        ).model_dump()
    )


def error_response(message: str, error: str = None, status_code: int = status.HTTP_400_BAD_REQUEST):
    """Create an error response"""
    return JSONResponse(
        status_code=status_code,
        content=StandardResponse(
            success=False,
            message=message,
            error=error or message
        ).model_dump()
    )


def handle_exception(exc: Exception) -> JSONResponse:
    """Handle application exceptions"""
    logger.error(f"Exception occurred: {exc}")
    
    if isinstance(exc, AppException):
        return error_response(exc.message, status_code=exc.status_code)
    
    return error_response(
        "An unexpected error occurred",
        str(exc),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
