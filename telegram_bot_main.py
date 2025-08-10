import os
import asyncio
import aiohttp
import json
import logging
from lore_manager import LoreManager

# Настройки
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

# Хранилище истории диалога
conversations = {}

SYSTEM_PROMPT = "Ты — ролевой персонаж. Общайся дружелюбно и интересно."

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.session = None
        self.lore_manager = LoreManager()
        
    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
            
    async def send_message(self, chat_id, text):
        """Отправить сообщение через Telegram API"""
        session = await self.get_session()
        url = f"{self.api_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        async with session.post(url, json=data) as response:
            result = await response.json()
            if not result.get("ok"):
                logger.error(f"Ошибка отправки сообщения: {result}")
            return result
            
    async def get_updates(self, offset=None):
        """Получить обновления от Telegram"""
        session = await self.get_session()
        url = f"{self.api_url}/getUpdates"
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset
            
        async with session.get(url, params=params) as response:
            return await response.json()
            
    async def get_deepseek_response(self, conversation_history):
        """Получить ответ от DeepSeek API"""
        session = await self.get_session()
        
        # Создаем системный промпт с лором
        system_prompt = self.lore_manager.get_system_prompt(SYSTEM_PROMPT)
        messages = [{"role": "system", "content": system_prompt}] + conversation_history
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        try:
            async with session.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    logger.error(f"DeepSeek API error {response.status}: {error_text}")
                    return "Извините, произошла ошибка при обращении к AI. Попробуйте позже."
                    
        except asyncio.TimeoutError:
            logger.error("DeepSeek API timeout")
            return "Извините, превышено время ожидания ответа. Попробуйте позже."
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            return "Извините, произошла ошибка при обращении к AI. Попробуйте позже."
            
    async def handle_message(self, message):
        """Обработать сообщение"""
        user_id = message["from"]["id"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        logger.info(f"Получено сообщение от пользователя {user_id}: {text[:50]}...")
        
        # Обработка команд
        if text.startswith("/start"):
            welcome_text = "Привет! Я умный помощник на базе DeepSeek AI. Просто напиши мне сообщение, и я отвечу!"
            await self.send_message(chat_id, welcome_text)
            return
            
        elif text.startswith("/reset"):
            conversations.pop(user_id, None)
            await self.send_message(chat_id, "История разговора сброшена!")
            return
            
        elif text.startswith("/help"):
            help_text = """
🤖 Ролевой бот с лором

Этот бот погружает вас в ролевую игру на основе загруженного лора. 

Доступные команды:
/start - начать работу с ботом
/reset - сбросить историю разговора
/help - показать это сообщение
/lore - информация о загруженном лоре
/reload_lore - перезагрузить лор из файлов

Бот запоминает контекст разговора и играет роль в соответствии с лором мира.
            """
            await self.send_message(chat_id, help_text)
            return
            
        elif text.startswith("/lore"):
            lore_info = self.lore_manager.get_lore_summary()
            await self.send_message(chat_id, f"📚 Лор: {lore_info}")
            return
            
        elif text.startswith("/reload_lore"):
            self.lore_manager.reload_lore()
            lore_info = self.lore_manager.get_lore_summary()
            await self.send_message(chat_id, f"🔄 Лор перезагружен: {lore_info}")
            return
        
        # Обработка обычных сообщений
        if not text or text.startswith("/"):
            return
            
        # Получить историю разговора
        history = conversations.setdefault(user_id, [])
        
        # Добавить сообщение пользователя
        history.append({"role": "user", "content": text})
        
        # Ограничить историю (оставить последние 50 сообщений)
        if len(history) > 50:
            conversations[user_id] = history[-50:]
            history = conversations[user_id]
        
        # Получить ответ от AI
        ai_response = await self.get_deepseek_response(history)
        
        # Добавить ответ AI в историю
        history.append({"role": "assistant", "content": ai_response})
        
        # Отправить ответ пользователю
        await self.send_message(chat_id, ai_response)
        
        logger.info(f"Отправлен ответ пользователю {user_id}")
        
    async def run(self):
        """Запустить бота"""
        logger.info("Запуск бота...")
        
        # Проверить токен
        if not TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN не найден")
            return
            
        if not DEEPSEEK_API_KEY:
            logger.error("DEEPSEEK_API_KEY не найден")
            return
        
        # Получить информацию о боте
        session = await self.get_session()
        async with session.get(f"{self.api_url}/getMe") as response:
            me = await response.json()
            if me.get("ok"):
                bot_info = me["result"]
                logger.info(f"Бот запущен: @{bot_info['username']} ({bot_info['first_name']})")
            else:
                logger.error(f"Ошибка получения информации о боте: {me}")
                return
        
        offset = None
        
        try:
            while True:
                # Получить обновления
                updates = await self.get_updates(offset)
                
                if not updates.get("ok"):
                    logger.error(f"Ошибка получения обновлений: {updates}")
                    await asyncio.sleep(5)
                    continue
                
                # Обработать каждое обновление
                for update in updates["result"]:
                    try:
                        # Обновить offset
                        offset = update["update_id"] + 1
                        
                        # Обработать сообщение
                        if "message" in update:
                            await self.handle_message(update["message"])
                            
                    except Exception as e:
                        logger.error(f"Ошибка обработки обновления {update['update_id']}: {e}")
                        
                # Если нет обновлений, подождать немного
                if not updates["result"]:
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            logger.info("Остановка бота...")
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
        finally:
            await self.close()

async def main():
    bot = TelegramBot(TELEGRAM_BOT_TOKEN)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())