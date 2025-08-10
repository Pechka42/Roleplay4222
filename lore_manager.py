import os
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class LoreManager:
    """Управление лором для ролевого бота"""
    
    def __init__(self, lore_files: List[str] = None):
        self.lore_files = lore_files or ["lore1.txt", "lore2.txt"]
        self.lore_content = ""
        self.load_lore()
    
    def load_lore(self):
        """Загрузить лор из файлов"""
        combined_lore = []
        
        for lore_file in self.lore_files:
            if os.path.exists(lore_file):
                try:
                    with open(lore_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content and not content.startswith('#'):  # Пропускаем заглушки
                            combined_lore.append(f"=== {lore_file} ===\n{content}")
                            logger.info(f"Загружен лор из {lore_file}: {len(content)} символов")
                except Exception as e:
                    logger.error(f"Ошибка загрузки лора из {lore_file}: {e}")
            else:
                logger.warning(f"Файл лора {lore_file} не найден")
        
        if combined_lore:
            self.lore_content = "\n\n".join(combined_lore)
            logger.info(f"Общий размер лора: {len(self.lore_content)} символов")
        else:
            logger.warning("Лор не загружен - файлы пусты или отсутствуют")
    
    def get_system_prompt(self, base_prompt: str = "") -> str:
        """Создать системный промпт с лором"""
        if not self.lore_content:
            return base_prompt
        
        lore_prompt = f"""
ВАЖНО: Ты ролевой персонаж в мире с данным лором. Следуй этому лору точно.

=== ЛОР МИРА ===
{self.lore_content}
=== КОНЕЦ ЛОРА ===

Инструкции:
1. Всегда оставайся в роли персонажа из этого мира
2. Используй информацию из лора для ответов
3. Не нарушай установленные правила мира
4. Если что-то не описано в лоре, импровизируй в рамках его логики
5. Общайся естественно, но в контексте этого мира

{base_prompt}
"""
        return lore_prompt
    
    def get_lore_summary(self) -> str:
        """Получить краткую сводку лора"""
        if not self.lore_content:
            return "Лор не загружен"
        
        word_count = len(self.lore_content.split())
        char_count = len(self.lore_content)
        
        return f"Загружено {len(self.lore_files)} файлов лора. Размер: {char_count} символов, {word_count} слов"
    
    def search_lore(self, query: str) -> List[str]:
        """Поиск релевантной информации в лоре"""
        if not self.lore_content or not query:
            return []
        
        # Простой поиск по ключевым словам
        query_words = query.lower().split()
        lines = self.lore_content.split('\n')
        relevant_lines = []
        
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in query_words):
                relevant_lines.append(line.strip())
        
        return relevant_lines[:10]  # Возвращаем максимум 10 релевантных строк
    
    def reload_lore(self):
        """Перезагрузить лор из файлов"""
        self.load_lore()