from typing import Dict, Any, Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, InlineQueryHandler

from src.auxiliary.bot_utils import stringify
from src.describe_sticker_handler import describe_sticker_conversation_handlers
from src.auxiliary.logger import logger
from src.describe_voice_handler import describe_voice_handlers
from src.groups_handler import groups_handlers
from src.list_content_handler import list_content_handlers
from src.pesistent_context.persistent_context_pymongo import PymongoConversationPersistence
from src.search_content import search_content
from src.start_handler import start_handler
from src.auxiliary.stopwatch import Stopwatch
from src.user_content_action_handlers import user_content_action_handlers

JSONDict = Dict[str, Any]


def _extract_user_id(message_data: dict) -> Optional[int]:
    if 'message' in message_data:
        key = 'message'
    elif 'inline_query' in message_data:
        key = 'inline_query'
    elif 'callback_query' in message_data:
        key = 'callback_query'
    else:
        return None

    return message_data[key]['from']['id']


async def handle_bot_request(bot_token: str, message_data: dict):
    if 'channel_post' in message_data and message_data['channel_post']['chat']['title'] == 'StickerFindingBroadcast':
        pass

    user_id = _extract_user_id(message_data)
    if user_id is None:
        return

    logger.info(f'Handling bot request for user {user_id}')

    application = Application.builder() \
        .token(bot_token) \
        .persistence(PymongoConversationPersistence(user_id=user_id)) \
        .build()

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", start_handler))
    application.add_handler(InlineQueryHandler(search_content))
    application.add_handlers(list(describe_sticker_conversation_handlers()))
    application.add_handlers(list(groups_handlers()))
    application.add_handlers(list(describe_voice_handlers()))
    application.add_handlers(list(list_content_handlers()))
    application.add_handlers(list(user_content_action_handlers()))

    on_finish = lambda delta: logger.info(f'User {user_id}: Request handling finished in {delta} seconds.')
    with Stopwatch(on_finish=on_finish):
        async with application:
            update = Update.de_json(data=message_data, bot=application.bot)
            logger.info(f'Processing request: {stringify(update)}.')
            await application.process_update(update)


async def setup_webhook(bot_token: str, url: str):
    application = Application.builder().token(bot_token).build()
    await application.bot.set_webhook(url=url)
