import asyncio
import logging

from aiogram import Bot

from motor.core import AgnosticDatabase as MDB


async def decrement_premium_days(bot: Bot, db: MDB):
    cursor = db.users.find({"current_plan": 1, "premium_days_remaining": {"$gt": 0}})
    users = await cursor.to_list(None)

    for user in users:
        new_days = user["premium_days_remaining"] - 1

        if new_days <= 0:
            await db.users.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "current_plan": 0,
                        "premium_days_remaining": None
                    }
                }
            )
            message = "Your premium plan has expired. You have been moved to the classic plan."
        else:
            db.users.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "premium_days_remaining": new_days
                    }
                }
            )
            message = f"Your premium plan has {new_days} days remaining."

        try:
            await bot.send_message(user["_id"], message)
        except Exception as e:
            logging.error(f"Failed to send message to user {user['_id']}: {e}")
        logging.info(f"Updated user {user['_id']} with {new_days} days remaining.")


async def increment_attempts(db: MDB):
    premium_users = db.users.find({
        "current_plan": 1
    })
    premium_users = await premium_users.to_list(None)

    classic_users = db.users.find({
        "current_plan": 0
    })
    classic_users = await classic_users.to_list(None)

    for user in premium_users:
        new_premium_attempts = user.get("premium_attempts", 0) + 20
        db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"premium_attempts": new_premium_attempts}}
        )
        logging.info(f"Incremented premium attempts for user {user['_id']} to {new_premium_attempts}")

    for user in classic_users:
        new_classic_attempts = user.get("classic_attempts", 0) + 20
        db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"classic_attempts": new_classic_attempts}}
        )
        logging.info(f"Incremented classic attempts for user {user['_id']} to {new_classic_attempts}")


async def daily_update(db: MDB, bot: Bot):
    await decrement_premium_days(db=db, bot=bot)
    await increment_attempts(db=db)


async def daily_check(db: MDB, bot: Bot):
    while True:
        logging.info("Running daily update for decrementing premium days and incrementing attempts.")
        await daily_update(db=db, bot=bot)
        await asyncio.sleep(86400)  # Sleep for 24 hours   
