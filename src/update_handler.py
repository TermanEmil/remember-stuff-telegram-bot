import logging
from typing import Dict, Any, Optional
from uuid import uuid4

from telegram import Update, InlineQueryResultCachedSticker
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes, \
    InlineQueryHandler

from src.models.user_content import save_user_content, UserContent, search_user_content
from src.persistent_context_pymongo import PymongoConversationPersistence

JSONDict = Dict[str, Any]


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello')


async def describe_sticker_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Okay, now send me some stickers!')
    return SEND_STICKERS


async def send_stickers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.sticker:
        await update.message.reply_text('Sticker required!')
        return SEND_STICKERS

    sticker_id = update.message.sticker.file_id
    context.user_data['conversation_sticker_id'] = sticker_id
    await update.message.reply_text(
        f"Adding sticker with id {sticker_id}.\n" +
        f"Now add some description."
    )

    return SEND_DESCRIPTION


async def send_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    sticker_id = context.user_data['conversation_sticker_id']
    description = update.message.text

    user_content = UserContent(
        user_id=user_id,
        content_id=sticker_id,
        description=description,
        groups=[f'user-{user_id}']
    )
    save_user_content(user_content)

    await update.message.reply_text(
        f"The sticker with id {sticker_id} saved with the following description: {description}\n" +
        "To start again use /describe_sticker"
    )
    await update.message.reply_sticker(
        sticker=sticker_id
    )
    return ConversationHandler.END


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Cancelled')
    return ConversationHandler.END


SEND_STICKERS, SEND_DESCRIPTION = range(2)


def describe_sticker_conversation() -> ConversationHandler:
    return ConversationHandler(
        name='describe_sticker_conversation',
        entry_points=[CommandHandler("describe_sticker", describe_sticker_handler)],
        states={
            SEND_STICKERS: [MessageHandler(filters.ALL, send_stickers_handler)],
            SEND_DESCRIPTION: [MessageHandler(filters.ALL, send_description_handler)]
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
        persistent=True,
        allow_reentry=True,
    )


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query

    if not query:  # empty query should not be handled
        return

    logging.info(f'Received inline query: {query}')
    items = search_user_content(query)
    logging.info(f'Found {len(items)} results')

    def map_to_query_result(item: UserContent):
        return InlineQueryResultCachedSticker(
            id=str(uuid4()),
            sticker_file_id=item['content_id']
        )

    results = [map_to_query_result(item) for item in items]
    await update.inline_query.answer(results)


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

    application = Application.builder()\
        .token(bot_token)\
        .persistence(PymongoConversationPersistence(user_id=user_id))\
        .build()

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(describe_sticker_conversation())
    application.add_handler(InlineQueryHandler(inline_query))

    async with application:
        update = Update.de_json(data=message_data, bot=application.bot)
        await application.process_update(update)

    pass


async def setup_webhook(bot_token: str, url: str):
    application = Application.builder().token(bot_token).build()
    await application.bot.set_webhook(url=url)
