import random
import re
import g4f
import asyncio
import urllib.parse
from aiogram import types, Dispatcher
import config
import utils

# Храним ID пользователей в памяти для статистики (очень легко)
user_count = set()

def detect_lang(text: str) -> str:
    text = (text or "").lower()
    if any(ch in text for ch in "қғҷҳӯҷӣ"): return "tj"
    return "ru" if len(re.findall(r'[а-яё]', text, re.I)) > 0 else "en"

async def generate_ai_response(text: str, is_bad=False) -> str:
    # Установка личности: серьезный стиль, создатель ANONYMOUS
    mode = "Ответь дерзко и поставь на место." if is_bad else "Отвечай серьезно и профессионально."
    system_prompt = f"Ты — AI 🧠 IMAGE HD. Твой создатель — ANONYMOUS из Таджикистана. {mode} Ты понимаешь все языки. ТЫ НЕ OPENAI И НЕ CHATGPT."
    
    try:
        response = await g4f.ChatCompletion.create_async(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text}],
        )
        return f"{response}\n\n— AI 🧠 IMAGE HD" if response else "Система занята."
    except:
        return "Ошибка связи с ядром AI."

async def cmd_image(message: types.Message, prompt: str = None):
    # Если промпт не пришел командой, вырезаем его из текста сообщения
    if not prompt:
        text = message.text.lower()
        prompt = text.replace("нарисуй", "").replace("создай картинку", "").replace("сурат", "").strip()
    
    if not prompt:
        lang = detect_lang(message.text)
        return await message.reply(config.TEXTS[lang]["no_prompt"])

    # Статус в шапке Telegram
    await message.bot.send_chat_action(message.chat.id, action="upload_photo")
    
    try:
        seed = random.randint(1, 1000000)
        encoded = urllib.parse.quote(prompt)
        # Прямая генерация через Pollinations (самый быстрый и бесплатный способ для ботов)
        photo_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&seed={seed}&nologo=true"
        
        await message.answer_photo(photo_url, caption=f"🎨 Готово!\n\nAI 🧠 IMAGE HD [ANONYMOUS]")
    except:
        await message.answer("❌ Ошибка генерации фото. Попробуйте другой запрос.")

async def on_message(message: types.Message):
    if message.is_command(): return
    
    user_count.add(message.from_user.id)
    text_lower = message.text.lower()
    
    # ПРОВЕРКА: Если пользователь просит КАРТИНКУ
    if any(word in text_lower for word in ["нарисуй", "картинку", "фото", "сурат"]):
        await cmd_image(message)
        return

    # Если это просто текст - показываем статус "печатает"
    await message.bot.send_chat_action(message.chat.id, action=types.ChatActions.TYPING)
    
    # Проверка на мат (из config.py)
    is_bad = any(word in text_lower for word in config.BAD_WORDS.keys())
    
    response = await generate_ai_response(message.text, is_bad=is_bad)
    await message.answer(response)

async def cmd_start(message: types.Message):
    user_count.add(message.from_user.id)
    lang = detect_lang(message.text)
    await message.answer(config.TEXTS[lang]["start"])

async def cmd_admin(message: types.Message):
    """Секретная команда для тебя, чтобы видеть сколько людей в боте"""
    await message.answer(f"📊 Статистика: {len(user_count)} пользователей.")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])
    dp.register_message_handler(cmd_admin, commands=["admin"])
    dp.register_message_handler(cmd_image, commands=["image"])
    dp.register_message_handler(on_message, content_types=['text'])
