"""
Retry Service - Handles retry logic with exponential backoff.
Manages failed notification retries and dead-letter handling.
"""

import asyncio
import logging
from typing import Callable, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class RetryService:
    """Service for managing notification retry logic."""

    def __init__(self):
        self.max_retries = settings.MAX_RETRY_COUNT
        self.backoff_base = settings.RETRY_BACKOFF_BASE
        self.initial_delay = settings.RETRY_INITIAL_DELAY

    def calculate_backoff_delay(self, retry_count: int) -> int:
        """Calculate exponential backoff delay in seconds."""
        delay = self.initial_delay * (self.backoff_base ** retry_count)
        return min(delay, 300)  # Cap at 5 minutes

    async def execute_with_retry(
        self,
        func: Callable,
        *args: Any,
        max_retries: int = None,
        **kwargs: Any,
    ) -> dict:
        """
        Execute a function with retry logic and exponential backoff.
        Returns dict with success status, result, and retry count.
        """
        retries = max_retries or self.max_retries
        last_error = None

        for attempt in range(retries + 1):
            try:
                result = await func(*args, **kwargs)
                return {
                    "success": True,
                    "result": result,
                    "attempts": attempt + 1,
                }
            except Exception as e:
                last_error = e
                if attempt < retries:
                    delay = self.calculate_backoff_delay(attempt)
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{retries} failed: {str(e)}. "
                        f"Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"All {retries} retry attempts exhausted. "
                        f"Last error: {str(e)}"
                    )

        return {
            "success": False,
            "error": str(last_error),
            "attempts": retries + 1,
            "dead_letter": True,
        }

    def should_retry(self, current_count: int, max_count: int = None) -> bool:
        """Check if a retry should be attempted."""
        max_allowed = max_count or self.max_retries
        return current_count < max_allowed
