"""
Custom exception classes and global exception handlers
for the ZenSeva Communication Service.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


class CommunicationServiceError(Exception):
    """Base exception for communication service."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotificationDeliveryError(CommunicationServiceError):
    """Raised when a notification fails to deliver."""

    def __init__(self, channel: str, recipient: str, reason: str):
        self.channel = channel
        self.recipient = recipient
        message = f"Failed to deliver {channel} notification to {recipient}: {reason}"
        super().__init__(message, status_code=502)


class TemplateNotFoundError(CommunicationServiceError):
    """Raised when a notification template is not found."""

    def __init__(self, template_id: str):
        message = f"Notification template '{template_id}' not found"
        super().__init__(message, status_code=404)


class RetryExhaustedError(CommunicationServiceError):
    """Raised when all retry attempts are exhausted."""

    def __init__(self, notification_id: str, max_retries: int):
        message = f"All {max_retries} retry attempts exhausted for notification {notification_id}"
        super().__init__(message, status_code=503)


class RateLimitExceededError(CommunicationServiceError):
    """Raised when rate limit is exceeded."""

    def __init__(self):
        super().__init__("Rate limit exceeded", status_code=429)
