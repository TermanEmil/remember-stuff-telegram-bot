from typing import Dict, Any, Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, \
    InlineQueryHandler

from src.describe_sticker_conversation import describe_sticker_conversation
from src.auxiliary.logger import logger
from src.pesistent_context.persistent_context_pymongo import PymongoConversationPersistence
from src.search_content import search_content

JSONDict = Dict[str, Any]


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello')


def _extract_user_id(message_data: dict) -> Optional[int]:
    if 'message' in message_data:
        key = 'message'
    elif 'inline_query' in message_data:
        key = 'inline_query'
    else:
        return None

    return message_data[key]['from']['id']


async def handle_bot_request(bot_token: str, message_data: dict):
    user_id = _extract_user_id(message_data)
    if user_id is None:
        return

    logger.info(f'Handling bot request for user {user_id}')

    application = Application.builder()\
        .token(bot_token)\
        .persistence(PymongoConversationPersistence(user_id=user_id))\
        .build()

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(describe_sticker_conversation())
    application.add_handler(InlineQueryHandler(search_content))

    async with application:
        update = Update.de_json(data=message_data, bot=application.bot)
        await application.process_update(update)

    logger.info(f'Finished handling bot request for user {user_id}')


async def setup_webhook(bot_token: str, url: str):
    application = Application.builder().token(bot_token).build()
    await application.bot.set_webhook(url=url)
