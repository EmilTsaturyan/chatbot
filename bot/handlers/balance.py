from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from motor.core import AgnosticDatabase as MDB


router = Router()


@router.message(Command('balance'))
async def balance(message: Message, db: MDB):
    user = await db.users.find_one({'_id': message.from_user.id})

    await message.answer(f'Your balance: {user["balance"]}')

    