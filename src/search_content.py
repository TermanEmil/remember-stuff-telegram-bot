from uuid import uuid4

from telegram import InlineQueryResultCachedSticker, Update
from telegram.ext import ContextTypes

from src.auxiliary.logger import logger
from src.user_content import UserContent, search_user_content


async def search_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query

    # Empty query should not be handled
    if not query:
        return

    logger.info(f'Received inline query: {query}')
    subscribed_groups = context.user_data.get('subscribed_groups')
    items = search_user_content(subscribed_groups, query)
    logger.info(f'Found {len(items)} results')

    def map_to_query_result(item: UserContent):
        return InlineQueryResultCachedSticker(
            id=str(uuid4()),
            sticker_file_id=item['content_file_id']
        )

    results = [map_to_query_result(item) for item in items]
    await update.inline_query.answer(results)
