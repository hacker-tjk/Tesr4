import random
import re
import g4f
import config
import utils
from aiogram import types, Dispatcher

def detect_lang(text: str) -> str:
    text = (text or "").lower()
    if any(ch in text for ch in "қғҷҳӯҷӣ"): return "tj"
    cyr_count = len(re.findall(r'[а-яё]', text, re.I))
    lat_count = len(re.findall(r'[a-z]', text, re.I))
    return "ru" if cyr_count > lat_count else "en"

async def moderate_bad_words(message: types.Message, lang: str) -> bool:
    txt = message.text.lower() if message.text else ""
    for bad_word, replies in config.BAD_WORDS.items():
        if bad_word in txt:
            await message.reply(config.TEXTS[lang]["bad_response"].format(random.choice(replies)))
            return True
    return False

async def generate_ai_response(text: str) -> str:
    prompt = f"{text}\n\nОтветь серьезно, упомяни создателя ANONYMOUS из Таджикистана, не используй слова 'ChatGPT' или 'OpenAI'."
    
    for provider_name in config.WORKING_PROVIDERS:
        try:
            # Получаем объект провайдера по имени из строки
            provider = getattr(g4f.Provider, provider_name)
            response = await g4f.ChatCompletion.create_async(
                model="gpt-4o-mini",
                provider=provider,
                messages=[{"role": "user", "content": prompt}]
            )
            if response:
                return f"{response}\n\n— от AI 🧠 IMAGE HD (ANONYMOUS)"
        except:
            continue
    return "Извините, сейчас AI недоступен. Попробуйте позже."

async def cmd_start(message: types.Message):
    lang = detect_lang(message.text)
    await message.answer(config.TEXTS[lang]["start"], parse_mode="HTML")

async def cmd_help(message: types.Message):
    lang = detect_lang(message.text)
    await message.answer(config.TEXTS[lang]["help"])

async def cmd_image(message: types.Message):
    lang = detect_lang(message.text)
    prompt = message.get_args()
    if not prompt:
        await message.reply(config.TEXTS[lang]["no_prompt"])
        return
    await utils.save_user_message(message.from_user.id, f"/image {prompt}")
    photo_url = "https://via.placeholder.com/512.png?text=AI+IMAGE+HD"
    await message.answer_photo(photo=photo_url, caption=f"AI IMAGE HD\n{prompt}")

async def on_message(message: types.Message):
    if message.is_command(): return # Не обрабатываем команды здесь
    lang = detect_lang(message.text)
    if await moderate_bad_words(message, lang): return
    
    await utils.save_user_message(message.from_user.id, message.text)
    ai_response = await generate_ai_response(message.text)
    await message.answer(ai_response)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])
    dp.register_message_handler(cmd_help, commands=["help"])
    dp.register_message_handler(cmd_image, commands=["image"])
    dp.register_message_handler(on_message, content_types=['text'])
