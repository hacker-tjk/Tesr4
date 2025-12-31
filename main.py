import asyncio
import logging_config
from bot import create_bot
import handlers

async def main():
    logging_config.setup_logging()
    bot, dp = create_bot()
    handlers.register_handlers(dp)
    print("Бот AI IMAGE HD запущен!")
    try:
        await dp.start_polling()
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
