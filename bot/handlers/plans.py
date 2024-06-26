from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from motor.core import AgnosticDatabase as MDB


router = Router()


@router.message(Command('current_plan'))
async def current_plan(message: Message, db: MDB):
    user = await db.users.find_one({'_id': message.from_user.id})
    plan = 'classic' if user['current_plan'] == 0 else 'premium'

    await message.answer(f'Your current plan is {plan}')


@router.message(Command('attempts'))
async def plans(message: Message, db: MDB):
    user = await db.users.find_one({'_id': message.from_user.id})
    
    await message.answer(f'You have: \n{user["classic_attempts"]} - classic attempts\n{user["premium_attempts"]} - premium attempts')