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
    prompt = f"{text}\n\nОтветь серьезно, упомяни создателя ANONYMOUS из Таджикистана."
    
    # Пытаемся использовать авто-выбор провайдера (самый надежный вариант)
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": prompt}],
        )
        if response and len(str(response)) > 2:
            return f"{response}\n\n— от AI 🧠 IMAGE HD"
    except Exception as e:
        print(f"Ошибка авто-провайдера: {e}")

    # Если не вышло, пробуем конкретные рабочие провайдеры
    for p_name in ["DuckDuckGo", "Bing", "Liaobots"]:
        try:
            prov = getattr(g4f.Provider, p_name)
            response = await g4f.ChatCompletion.create_async(
                model="gpt-4o-mini",
                provider=prov,
                messages=[{"role": "user", "content": prompt}]
            )
            if response:
                return f"{response}\n\n— от AI 🧠 IMAGE HD"
        except:
            continue
            
    return "Извините, сейчас серверы перегружены. Попробуйте через минуту."

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
    # Заглушка для фото, так как g4f для картинок требует сложной настройки
    await message.answer(f"🎨 Запрос на генерацию принят: {prompt}\n(Функция генерации фото настраивается)")

async def on_message(message: types.Message):
    if message.is_command(): return 
    lang = detect_lang(message.text)
    if await moderate_bad_words(message, lang): return
    
    await utils.save_user_message(message.from_user.id, message.text)
    ai_response = await generate_ai_response(message.text)
    await message.answer(ai_response)

# ТА САМАЯ ФУНКЦИЯ, КОТОРОЙ НЕ ХВАТАЛО
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])
    dp.register_message_handler(cmd_help, commands=["help"])
    dp.register_message_handler(cmd_image, commands=["image"])
    dp.register_message_handler(on_message, content_types=['text'])
