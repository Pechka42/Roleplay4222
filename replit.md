# Overview

This is a Telegram bot application that integrates with DeepSeek AI to provide conversational AI responses. The bot maintains conversation history for multiple users and is currently running as @Roleplay42postapBot. It's built using direct Telegram Bot API calls with aiohttp for efficient asynchronous handling of multiple concurrent conversations.

## Recent Changes (August 10, 2025)
- Successfully resolved python-telegram-bot package conflicts by creating a simplified implementation using direct Telegram API calls
- Bot is now live and running as @Roleplay42postapBot with proper DeepSeek AI integration
- **MAJOR UPDATE**: Integrated extensive lore system for post-apocalyptic roleplay in Russia 2031
- Loaded 126,044 characters of worldbuilding lore across two documents (lore1.txt, lore2.txt)
- Added lore management system with LoreManager class for dynamic lore integration
- Added specialized commands: /lore, /reload_lore for lore management
- Bot now operates as roleplay game master in established post-apocalyptic world with characters like Йонас, Глеб, Виктор, Шрамыч, and Dr. Сардов

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **Direct Telegram API**: Uses direct HTTP calls to Telegram Bot API via aiohttp for maximum compatibility and control
- **Command Processing**: Implements command handlers (`/start`, `/reset`, `/help`) and message processing in working_bot.py
- **Asynchronous Processing**: All operations are async to handle multiple users concurrently without blocking
- **Long Polling**: Uses Telegram's getUpdates API with long polling for real-time message reception

## AI Integration
- **DeepSeek API Client**: Custom HTTP client using `aiohttp` for making API calls to DeepSeek's chat completions endpoint
- **System Prompts**: Configurable system prompts (default in Russian) to define AI personality and behavior
- **Request/Response Management**: Handles API timeouts, error handling, and response parsing

## Conversation Management
- **Per-User History**: Maintains separate conversation history for each Telegram user ID
- **Memory Management**: Automatically trims conversation history when it exceeds configured limits (default 50 messages)
- **Message Roles**: Tracks user and assistant messages in OpenAI-compatible format

## Security & Error Handling
- **Environment Variable Validation**: Validates required API keys (TELEGRAM_BOT_TOKEN, DEEPSEEK_API_KEY) on startup
- **Comprehensive Error Handling**: Handles API timeouts, network errors, and malformed responses gracefully
- **Conversation Limits**: Automatically trims conversation history to last 50 messages per user to manage memory

## Configuration Management
- **Environment-Based Config**: All settings configurable via environment variables
- **Validation System**: Startup validation ensures required API keys and tokens are present
- **Flexible Deployment**: Easy to deploy across different environments with different configurations

# External Dependencies

## Required Services
- **Telegram Bot API**: Requires `TELEGRAM_BOT_TOKEN` for bot authentication and message handling
- **DeepSeek API**: Requires `DEEPSEEK_API_KEY` for AI conversation generation at `https://api.deepseek.com/chat/completions`

## Python Libraries
- **python-telegram-bot**: Telegram Bot API wrapper for handling updates and responses
- **aiohttp**: Async HTTP client for making API requests to DeepSeek
- **asyncio**: Built-in Python async framework for concurrent operations

## Environment Variables
- `TELEGRAM_BOT_TOKEN` (required): Bot authentication token from BotFather
- `DEEPSEEK_API_KEY` (required): API key for DeepSeek service
- `DEEPSEEK_URL` (optional): Custom API endpoint URL
- `DEEPSEEK_MODEL` (optional): Model name for AI responses
- `SYSTEM_PROMPT` (optional): Custom system prompt for AI personality
- `MAX_HISTORY_LENGTH` (optional): Maximum conversation history length
- `REQUEST_TIMEOUT` (optional): API request timeout in seconds
- `MAX_REQUESTS_PER_MINUTE` (optional): Rate limiting threshold per user