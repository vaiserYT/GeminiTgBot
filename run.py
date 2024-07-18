from aiogram import Dispatcher, Bot
import asyncio
import logging
import os
from apps.handlers import router
from dotenv import load_dotenv


DEBUG_MODE = True
load_dotenv()
bot = Bot(os.getenv('bot_token'))
dp = Dispatcher()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    dp.include_router(router)
    if DEBUG_MODE:
        logging.basicConfig(level=logging.INFO)
    asyncio.run(main())