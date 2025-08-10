"""
Configuration module for the Telegram bot.
"""

import os
from typing import Optional

class Config:
    """Configuration class for bot settings."""
    
    def __init__(self):
        # Telegram Bot Configuration
        self.TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
        
        # DeepSeek API Configuration
        self.DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
        self.DEEPSEEK_URL: str = os.getenv(
            "DEEPSEEK_URL", 
            "https://api.deepseek.com/chat/completions"
        )
        self.DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        # Bot Configuration
        self.SYSTEM_PROMPT: str = os.getenv(
            "SYSTEM_PROMPT",
            "Ты — ролевой персонаж. Общайся дружелюбно и интересно."
        )
        
        # Conversation limits
        self.MAX_HISTORY_LENGTH: int = int(os.getenv("MAX_HISTORY_LENGTH", "50"))
        self.REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
        
        # Rate limiting
        self.MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "10"))
        
    def validate(self) -> bool:
        """Validate required configuration parameters."""
        required_vars = [
            ("TELEGRAM_BOT_TOKEN", self.TELEGRAM_BOT_TOKEN),
            ("DEEPSEEK_API_KEY", self.DEEPSEEK_API_KEY)
        ]
        
        for var_name, var_value in required_vars:
            if not var_value:
                return False
        
        return True
