import math
import re
from typing import Iterable

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes

from src.user_content import get_all_user_described_content, STICKER_CONTENT, VOICE_MESSAGE_CONTENT
from src.user_content_action_handlers import send_user_content_with_callback_actions


async def list_my_contents_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        content_type: str,
        command_name: str
) -> None:
    text = re.sub(r'^/\w+', '', update.message.text).strip()
    match = re.search(r'page (\d+)', text, re.IGNORECASE)
    if match:
        page = int(match.group(1))
    else:
        page = 1

    user_id = update.message.from_user.id
    contents = get_all_user_described_content(user_id, content_type)

    page_size = 10
    keys = list(contents.keys())
    paginated_keys = keys[(page - 1) * page_size:page * page_size]
    paginated_contents = {key: contents[key] for key in paginated_keys}
    total_pages = int(math.ceil(len(contents) / page_size))
    has_next = (page + 1) * page_size <= len(contents)

    if len(contents) == 0:
        await update.message.reply_text('The list is empty.')
        return

    for contents in paginated_contents.values():
        await send_user_content_with_callback_actions(update, contents)

    if has_next:
        buttons = [[f'/{command_name} page {page + 1}']]
        keyboard = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f'Press the button to view the next ones.\nCurrently at {page}/{total_pages}.',
            reply_markup=keyboard
        )


async def list_my_stickers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await list_my_contents_handler(update, context, STICKER_CONTENT, 'list_my_stickers')


async def list_my_voices_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await list_my_contents_handler(update, context, VOICE_MESSAGE_CONTENT, 'list_my_voices')


def list_content_handlers() -> Iterable[CommandHandler]:
    yield CommandHandler('list_my_stickers', list_my_stickers_handler)
    yield CommandHandler('list_my_voices', list_my_voices_handler)
