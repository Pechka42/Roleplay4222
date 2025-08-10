"""
DeepSeek API client for generating AI responses.
"""

import logging
import asyncio
import aiohttp
from typing import List, Dict, Any
from config import Config

logger = logging.getLogger(__name__)

class DeepSeekClient:
    """Client for interacting with DeepSeek API."""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.REQUEST_TIMEOUT)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def get_response(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Get AI response from DeepSeek API.
        
        Args:
            conversation_history: List of message dictionaries with 'role' and 'content'
            
        Returns:
            AI response text
            
        Raises:
            Exception: If API request fails
        """
        try:
            # Prepare the payload
            messages = [
                {"role": "system", "content": self.config.SYSTEM_PROMPT}
            ] + conversation_history
            
            payload = {
                "model": self.config.DEEPSEEK_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            headers = {
                "Authorization": f"Bearer {self.config.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            session = await self._get_session()
            
            logger.debug(f"Sending request to DeepSeek API with {len(messages)} messages")
            
            async with session.post(
                self.config.DEEPSEEK_URL,
                json=payload,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    ai_response = data["choices"][0]["message"]["content"]
                    logger.debug(f"Received response: {ai_response[:100]}...")
                    return ai_response
                
                elif response.status == 401:
                    error_msg = "Ошибка авторизации. Проверьте API ключ DeepSeek."
                    logger.error(f"DeepSeek API authorization failed: {response.status}")
                    raise Exception(error_msg)
                
                elif response.status == 429:
                    error_msg = "Превышен лимит запросов к DeepSeek API. Попробуйте позже."
                    logger.error(f"DeepSeek API rate limit exceeded: {response.status}")
                    raise Exception(error_msg)
                
                else:
                    error_text = await response.text()
                    error_msg = f"Ошибка DeepSeek API (код {response.status}). Попробуйте позже."
                    logger.error(f"DeepSeek API error {response.status}: {error_text}")
                    raise Exception(error_msg)
                    
        except asyncio.TimeoutError:
            error_msg = "Превышено время ожидания ответа от DeepSeek API."
            logger.error("DeepSeek API request timeout")
            raise Exception(error_msg)
            
        except aiohttp.ClientError as e:
            error_msg = "Ошибка соединения с DeepSeek API."
            logger.error(f"DeepSeek API connection error: {e}")
            raise Exception(error_msg)
            
        except Exception as e:
            if "Ошибка" in str(e):
                # Re-raise our custom error messages
                raise e
            else:
                error_msg = "Неизвестная ошибка при обращении к DeepSeek API."
                logger.error(f"Unexpected DeepSeek API error: {e}")
                raise Exception(error_msg)
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
