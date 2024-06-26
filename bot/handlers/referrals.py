from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from motor.core import AgnosticDatabase as MDB


router = Router()


router.message(Command('get_referral_link'))
async def get_referral_link(message: Message, db: MDB):
    referral_link = f'https://t.me/QeyLogerBot/?start={message.from_user.id}'

    await message.answer(f'Your referral link\n{referral_link}')


