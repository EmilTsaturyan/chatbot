from contextlib import suppress

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from motor.core import AgnosticDatabase as MDB
from pymongo.errors import DuplicateKeyError

router = Router()


@router.message(CommandStart())
async def start(message: Message, db: MDB):
    pattern = {
        "_id": message.from_user.id,
        "balance": 0,
        "current_plan": 0,
        "classic_attempts": 50,
        "premium_attempts": 0,
        "premium_days_remaining": None,
        "referrals": 0,
        "referrer_id": None,
    }
    
    with suppress(DuplicateKeyError):
        await db.users.insert_one(pattern)

        if len(message.text.split(' ')) == 2:
            referral_id = int(message.text.split(' ')[-1])
            if referral_id != message.from_user.id:
                referrer = await db.users.find_one({'_id': referral_id})
                if referrer:
                    await db.users.update_one({'_id': referrer['_id']}, {'$set': {'referrals': referrer['referrals'] + 1}})
                    await db.users.update_one({'_id': message.from_user.id}, {'$set': {'referrer_id': referrer['_id']}})

    await message.answer(f'Welcome')
