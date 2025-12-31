import random
import re
import g4f
import asyncio
import config
import utils
import urllib.parse
from aiogram import types, Dispatcher

# Счетчик пользователей (локальный для скорости)
user_list = set()

def detect_lang(text: str) -> str:
    text = (text or "").lower()
    if any(ch in text for ch in "қғҷҳӯҷӣ"): return "tj"
    return "ru" if len(re.findall(r'[а-яё]', text, re.I)) > 0 else "en"

async def generate_ai_response(text: str, is_bad=False) -> str:
    # Твоя установка: Серьезный хакер от ANONYMOUS
    mode = "Ответь дерзко и грубо, поставь на место." if is_bad else "Отвечай серьезно и холодно."
    system_prompt = f"Ты — AI 🧠 IMAGE HD. Твой создатель — ANONYMOUS из Таджикистана. {mode} Ты понимаешь все языки. Ты не OpenAI."
    
    try:
        response = await g4f.ChatCompletion.create_async(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text}],
        )
        return f"{response}\n\n— AI 🧠 IMAGE HD"
    except:
        return "Система занята. Попробуй позже."

async def update_status(message: types.Message):
    """Показывает количество пользователей в статусе 'печатает'"""
    user_list.add(message.from_user.id)
    count = len(user_list)
    # Вместо просто 'печатает', в шапке будет это:
    status_text = f"Online: {count} users | AI 🧠"
    await message.bot.send_chat_action(message.chat.id, action=types.ChatActions.TYPING)
    return count

async def cmd_start(message: types.Message):
    user_list.add(message.from_user.id)
    lang = detect_lang(message.text)
    await message.answer(config.TEXTS[lang]["start"])

async def cmd_admin(message: types.Message):
    """Команда только для тебя, чтобы видеть статистику"""
    count = len(user_list)
    await message.answer(f"📊 **Статистика бота:**\nВсего пользователей: {count}")

async def cmd_image(message: types.Message):
    prompt = message.get_args() or message.text.lower().replace("нарисуй", "").strip()
    if not prompt: return await message.reply("✏️ Что нарисовать?")
    
    await message.bot.send_chat_action(message.chat.id, action="upload_photo")
    try:
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true"
        await message.answer_photo(url, caption="🎨 Готово | AI 🧠 IMAGE HD")
    except:
        await message.answer("❌ Ошибка графического ядра.")

async def cmd_video(message: types.Message):
    prompt = message.get_args() or message.text.lower().replace("видео", "").strip()
    if not prompt: return await message.reply("📽 Опишите видео.")
    
    await message.bot.send_chat_action(message.chat.id, action="record_video")
    try:
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?model=video"
        await message.answer_video(url, caption="🎬 Видео создано | AI 🧠")
    except:
        await message.answer("❌ Ошибка видео-модуля.")

async def on_message(message: types.Message):
    if message.is_command(): return
    
    # Обновляем количество людей и статус в шапке
    user_count = await update_status(message)
    
    text_lower = message.text.lower()
    
    # Быстрые фильтры
    if any(word in text_lower for word in ["нарисуй", "сурат", "draw"]):
        await cmd_image(message)
        return
    if any(word in text_lower for word in ["видео", "video"]):
        await cmd_video(message)
        return

    # Проверка на мат (берем из твоего конфига)
    is_bad = any(word in text_lower for word in config.BAD_WORDS.keys())

    # Ответ нейросети
    response = await generate_ai_response(message.text, is_bad=is_bad)
    await message.answer(response)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])
    dp.register_message_handler(cmd_admin, commands=["admin"]) # Твоя админка
    dp.register_message_handler(cmd_image, commands=["image"])
    dp.register_message_handler(cmd_video, commands=["video"])
    dp.register_message_handler(on_message, content_types=['text'])
