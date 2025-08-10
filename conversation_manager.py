"""
Conversation history management for multiple users.
"""

import logging
from typing import Dict, List, Any
from collections import defaultdict
from config import Config

logger = logging.getLogger(__name__)

class ConversationManager:
    """Manages conversation history for multiple users."""
    
    def __init__(self, config: Config):
        self.config = config
        self.conversations: Dict[int, List[Dict[str, str]]] = defaultdict(list)
    
    def add_message(self, user_id: int, role: str, content: str):
        """
        Add a message to user's conversation history.
        
        Args:
            user_id: Telegram user ID
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        if role not in ['user', 'assistant']:
            logger.warning(f"Invalid role '{role}' for user {user_id}")
            return
        
        conversation = self.conversations[user_id]
        conversation.append({
            "role": role,
            "content": content
        })
        
        # Trim conversation if it exceeds max length
        if len(conversation) > self.config.MAX_HISTORY_LENGTH:
            # Keep the most recent messages
            self.conversations[user_id] = conversation[-self.config.MAX_HISTORY_LENGTH:]
            logger.debug(f"Trimmed conversation for user {user_id} to {self.config.MAX_HISTORY_LENGTH} messages")
        
        logger.debug(f"Added {role} message for user {user_id}. History length: {len(self.conversations[user_id])}")
    
    def get_conversation(self, user_id: int) -> List[Dict[str, str]]:
        """
        Get conversation history for a user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            List of message dictionaries
        """
        return self.conversations[user_id].copy()
    
    def reset_conversation(self, user_id: int):
        """
        Reset conversation history for a user.
        
        Args:
            user_id: Telegram user ID
        """
        if user_id in self.conversations:
            del self.conversations[user_id]
            logger.info(f"Reset conversation for user {user_id}")
        else:
            logger.debug(f"No conversation to reset for user {user_id}")
    
    def get_conversation_count(self, user_id: int) -> int:
        """
        Get the number of messages in user's conversation.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Number of messages in conversation
        """
        return len(self.conversations[user_id])
    
    def get_active_users_count(self) -> int:
        """
        Get the number of users with active conversations.
        
        Returns:
            Number of active users
        """
        return len(self.conversations)
    
    def cleanup_empty_conversations(self):
        """Remove empty conversations to free memory."""
        empty_users = [user_id for user_id, messages in self.conversations.items() if not messages]
        for user_id in empty_users:
            del self.conversations[user_id]
        
        if empty_users:
            logger.info(f"Cleaned up {len(empty_users)} empty conversations")
