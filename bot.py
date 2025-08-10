"""
Main Telegram bot implementation with DeepSeek AI integration.
"""

import logging
from typing import Dict, Any
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    ContextTypes, 
    filters
)

from config import Config
from deepseek_client import DeepSeekClient
from conversation_manager import ConversationManager
from utils import RateLimiter

logger = logging.getLogger(__name__)

class TelegramBot:
    """Main Telegram bot class."""
    
    def __init__(self, config: Config):
        self.config = config
        self.deepseek_client = DeepSeekClient(config)
        self.conversation_manager = ConversationManager(config)
        self.rate_limiter = RateLimiter(config.MAX_REQUESTS_PER_MINUTE)
        
        # Build the application
        self.application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup bot command and message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("reset", self.reset_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Message handler for text messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        logger.info("Bot handlers configured")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user_id = update.effective_user.id
        username = update.effective_user.first_name or "пользователь"
        
        logger.info(f"User {user_id} started the bot")
        
        welcome_message = (
            f"Привет, {username}! 👋\n\n"
            "Я — умный помощник на базе DeepSeek AI. "
            "Просто напиши мне сообщение, и я отвечу!\n\n"
            "Команды:\n"
            "/start - показать это сообщение\n"
            "/reset - сбросить историю разговора\n"
            "/help - получить помощь"
        )
        
        await update.message.reply_text(welcome_message)
    
    async def reset_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reset command."""
        user_id = update.effective_user.id
        
        logger.info(f"User {user_id} reset conversation")
        
        self.conversation_manager.reset_conversation(user_id)
        await update.message.reply_text(
            "✅ История разговора сброшена! Можем начать заново."
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = (
            "🤖 Помощь по использованию бота\n\n"
            "Этот бот использует DeepSeek AI для генерации ответов. "
            "Просто напишите любое сообщение, и я отвечу!\n\n"
            "Доступные команды:\n"
            "/start - начать работу с ботом\n"
            "/reset - сбросить историю разговора\n"
            "/help - показать это сообщение\n\n"
            "Бот запоминает контекст разговора, поэтому можете задавать "
            "уточняющие вопросы или продолжать тему."
        )
        
        await update.message.reply_text(help_message)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages."""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Check rate limiting
        if not self.rate_limiter.is_allowed(user_id):
            await update.message.reply_text(
                "⚠️ Слишком много запросов. Подождите немного перед отправкой следующего сообщения."
            )
            return
        
        logger.info(f"Processing message from user {user_id}: {message_text[:50]}...")
        
        # Show typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, 
            action="typing"
        )
        
        try:
            # Add user message to conversation history
            self.conversation_manager.add_message(user_id, "user", message_text)
            
            # Get conversation history
            conversation_history = self.conversation_manager.get_conversation(user_id)
            
            # Get AI response
            ai_response = await self.deepseek_client.get_response(conversation_history)
            
            # Add AI response to conversation history
            self.conversation_manager.add_message(user_id, "assistant", ai_response)
            
            # Send response to user
            await update.message.reply_text(ai_response)
            
            logger.info(f"Successfully responded to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error processing message from user {user_id}: {e}")
            
            error_message = (
                "😔 Извините, произошла ошибка при обработке вашего сообщения. "
                "Попробуйте еще раз или используйте /reset для сброса истории."
            )
            
            await update.message.reply_text(error_message)
    
    async def start(self):
        """Start the bot."""
        logger.info("Bot is starting...")
        await self.application.initialize()
await self.application.start()
await self.application.updater.start_polling()
await self.application.updater.idle()
