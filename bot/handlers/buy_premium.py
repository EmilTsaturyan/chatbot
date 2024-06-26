

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from motor.core import AgnosticDatabase as MDB


router = Router()


@router.message(Command('buy_premium'))
async def buy_premium(message: Message, db: MDB):
    user = await db.users.find_one({'_id': message.from_user.id})

    if user['current_plan'] == 0:
        await db.users.update_one({'_id': user['_id']}, {'$set': {
            'current_plan': 1, 
            'premium_days_remaining': 30,
            'premium_attempts': 50
            }})
        await message.answer('Congrats!')
        if user['referrer_id']:
            referrer = await db.users.find_one({'_id': user['referrer_id']})
            if referrer:
                await db.users.update_one({'_id': referrer['_id']}, {'$set': {'balance': referrer['balance'] + 100}})
    else:
        await message.answer('You already have premium')