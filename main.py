import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config
import handlers

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=config.TOKEN, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация команд
    handlers.register_handlers(dp)

    print("Бот запущен и готов к работе!")
    try:
        await dp.start_polling()
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
