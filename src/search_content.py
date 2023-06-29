from uuid import uuid4

from telegram import InlineQueryResultCachedSticker, Update, InlineQueryResultCachedVoice
from telegram.ext import ContextTypes

from src.auxiliary.logger import logger
from src.user_content import UserContent, search_user_content, VOICE_MESSAGE_CONTENT, STICKER_CONTENT


async def search_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query

    # Empty query should not be handled
    if not query:
        return

    if query.startswith('voice'):
        query = query.removeprefix('voice')
        content_type = VOICE_MESSAGE_CONTENT
    else:
        query = query.removeprefix('sticker')
        content_type = STICKER_CONTENT

    query = query.strip()
    if len(query) <= 2:
        await update.inline_query.answer([])
        return

    logger.info(f'Received inline query: {query}')
    subscribed_groups = context.user_data.get('subscribed_groups')
    items = search_user_content(subscribed_groups, query, content_type)
    logger.info(f'Found {len(items)} results')

    def map_to_query_result(item: UserContent):
        if item['type'] == STICKER_CONTENT:
            return InlineQueryResultCachedSticker(
                id=str(uuid4()),
                sticker_file_id=item['content_file_id']
            )
        elif item['type'] == VOICE_MESSAGE_CONTENT:
            return InlineQueryResultCachedVoice(
                id=str(uuid4()),
                title=item['title'],
                voice_file_id=item['content_file_id']
            )
        else:
            raise Exception()

    results = map(lambda x: map_to_query_result(x), items)
    await update.inline_query.answer(list(results))
