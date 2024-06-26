import asyncio
import logging

from aiogram import Bot, Dispatcher

from handlers import base_commands, buy_premium, balance, chatbot, referrals, plans
from bot.daily_check import daily_check
from bot.config_reader import config

from motor.motor_asyncio import AsyncIOMotorClient


async def main():
    bot = Bot(config.bot_token.get_secret_value())
    dp = Dispatcher()

    dp.include_routers(
        base_commands.router,
        buy_premium.router,
        referrals.router,
        balance.router,
        plans.router,
        chatbot.router
        )

    cluster = AsyncIOMotorClient(host='localhost', port=27017)
    db = cluster.chatbot

    loop = asyncio.get_event_loop()
    loop.create_task(daily_check(db=db, bot=bot))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, db=db)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())