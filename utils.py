"""
Utility functions and classes for the Telegram bot.
"""

import time
import logging
from collections import defaultdict, deque
from typing import Dict, Deque

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter to prevent spam."""
    
    def __init__(self, max_requests_per_minute: int):
        self.max_requests = max_requests_per_minute
        self.requests: Dict[int, Deque[float]] = defaultdict(deque)
    
    def is_allowed(self, user_id: int) -> bool:
        """
        Check if user is allowed to make a request.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if request is allowed, False otherwise
        """
        current_time = time.time()
        user_requests = self.requests[user_id]
        
        # Remove requests older than 1 minute
        while user_requests and current_time - user_requests[0] > 60:
            user_requests.popleft()
        
        # Check if user has exceeded the limit
        if len(user_requests) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return False
        
        # Add current request
        user_requests.append(current_time)
        return True
    
    def cleanup_old_entries(self):
        """Clean up old rate limiting entries to free memory."""
        current_time = time.time()
        users_to_cleanup = []
        
        for user_id, requests in self.requests.items():
            # Remove old requests
            while requests and current_time - requests[0] > 60:
                requests.popleft()
            
            # Mark user for cleanup if no recent requests
            if not requests:
                users_to_cleanup.append(user_id)
        
        # Remove users with no recent requests
        for user_id in users_to_cleanup:
            del self.requests[user_id]
        
        if users_to_cleanup:
            logger.debug(f"Cleaned up rate limiting data for {len(users_to_cleanup)} users")

def format_error_message(error: Exception) -> str:
    """
    Format error message for user display.
    
    Args:
        error: Exception object
        
    Returns:
        User-friendly error message
    """
    error_str = str(error)
    
    # If it's already a user-friendly message (contains Russian text), return as is
    if any(ord(char) > 127 for char in error_str):
        return error_str
    
    # Default error message for technical errors
    return "Произошла техническая ошибка. Попробуйте позже или обратитесь к администратору."

def sanitize_message(message: str, max_length: int = 4000) -> str:
    """
    Sanitize and truncate message for Telegram.
    
    Args:
        message: Message to sanitize
        max_length: Maximum message length
        
    Returns:
        Sanitized message
    """
    if not message:
        return "Пустой ответ"
    
    # Remove any potentially harmful characters
    sanitized = message.strip()
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length - 3] + "..."
    
    return sanitized
