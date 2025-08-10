import logging
import asyncio
from bot import TelegramBot
from config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to start the bot."""
    try:
        # Load configuration
        config = Config()
        
        # Validate required environment variables
        if not config.TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
            return
            
        if not config.DEEPSEEK_API_KEY:
            logger.error("DEEPSEEK_API_KEY environment variable is required")
            return
        
        # Initialize and start the bot
        bot = TelegramBot(config)
        logger.info("Starting Telegram bot...")
        await bot.start()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    import asyncio
    import nest_asyncio

    async def main_wrapper():
        bot = TelegramBot(Config())
        await bot.start()

    try:
        asyncio.run(main_wrapper())
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            nest_asyncio.apply()
            loop = asyncio.get_event_loop()
            loop.create_task(main_wrapper())
            loop.run_forever()
        else:
            raise
