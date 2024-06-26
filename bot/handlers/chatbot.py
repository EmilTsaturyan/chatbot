from aiogram import Router
from aiogram.types import Message
from aiogram.enums import ParseMode

from motor.core import AgnosticDatabase as MDB

from freeGPT import Client


router = Router()


@router.message()
async def handle_gpt_query(message: Message, db: MDB):
    user_id = message.from_user.id
    user = await db.users.find_one({'_id': user_id})

    plan = determine_plan(user=user)

    if plan == -1:
        await message.answer('You don\'t have any attempts left.')
        return

    await update_attempts(db, user, plan)

    response = generate_gpt_response(message.text, 'gpt3_5')
    snippets = classify_text_and_code(response)

    await send_responses(message, snippets)


def generate_gpt_response(prompt, model):
    resp = Client.create_completion(model, prompt)
    return resp


def classify_text_and_code(text):
    """
    This function takes a string with mixed text and code blocks,
    and returns a list where each element is a list containing two items:
    the text or code block and a flag (0 for text, 1 for code).

    The code block is returned in the format [```language code snippet ```, 1].

    :param text: A string containing both regular text and code blocks.
    :return: A list of lists, each containing a string and a flag (0 for text, 1 for code).
    """
    lines = text.splitlines()
    result = []
    current_block = []
    is_code_block = False
    language = ''

    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith("```"):
            if is_code_block:  
                code_block = "\n".join(current_block)
                result.append([f"```{language}\n{code_block}\n```", 1])
                current_block = []
                language = ''
            else:  
                if current_block: 
                    result.append(["\n".join(current_block), 0])
                    current_block = []
                language = line_stripped[3:].strip()  
            is_code_block = not is_code_block
        else:
            current_block.append(line)
    
    if current_block: 
        result.append(["\n".join(current_block), 1 if is_code_block else 0])

    return result


def determine_plan(user: dict):
    if user['current_plan'] == 0:
        if user['premium_attempts'] > 0:
            return 1
        elif user['classic_attempts'] > 0:
            return 0
    else:
        if user['premium_attempts'] > 0:
            return 1
        elif user['classic_attempts'] > 0:
            return 0
    return -1


async def update_attempts(db: MDB, user: dict, plan: int):
    if plan == 0:
        new_attempts = user['classic_attempts'] - 1
        await db.users.update_one({'_id': user['_id']}, {'$set': {'classic_attempts': new_attempts}})
    elif plan == 1:
        new_attempts = user['premium_attempts'] - 1
        await db.users.update_one({'_id': user['_id']}, {'$set': {'premium_attempts': new_attempts}})


async def send_responses(message: Message, snippets: list[list[str, int]]):
    for snippet, is_markdown in snippets:
        if is_markdown:
            await message.answer(snippet, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await message.answer(snippet)


