import math
import re
from typing import Iterable, Dict, Tuple, List, Callable

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes

from src.user_content import get_all_user_described_content, STICKER_CONTENT, VOICE_MESSAGE_CONTENT, UserContent, \
    get_all_available_contents
from src.user_content_action_handlers import send_user_content_with_callback_actions


def _paginate(page: int, contents: Dict[str, List[UserContent]]) -> Tuple[Dict[str, List[UserContent]], int, bool]:
    page_size = 10
    keys = list(contents.keys())
    paginated_keys = keys[(page - 1) * page_size:page * page_size]
    paginated_contents = {key: contents[key] for key in paginated_keys}
    total_pages = int(math.ceil(len(contents) / page_size))
    has_next = page < total_pages

    return paginated_contents, total_pages, has_next


async def list_my_contents_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        contents_provider: Callable[[], Dict[str, List[UserContent]]],
        command_name: str
) -> None:
    text = re.sub(r'^/\w+', '', update.message.text).strip()
    match = re.search(r'page (\d+)', text, re.IGNORECASE)
    if match:
        page = int(match.group(1))
    else:
        page = 1

    contents = contents_provider()
    paginated_contents, total_pages, has_next = _paginate(page, contents)

    if len(contents) == 0:
        await update.message.reply_text('The list is empty.')
        return

    for contents in paginated_contents.values():
        await send_user_content_with_callback_actions(update, context, contents)

    if has_next:
        buttons = [[f'/{command_name} page {page + 1}']]
        keyboard = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f'Press the button to view the next ones.\nCurrently at {page}/{total_pages}.',
            reply_markup=keyboard
        )


async def list_my_stickers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await list_my_contents_handler(
        update,
        context,
        lambda: get_all_user_described_content(update.message.from_user.id, STICKER_CONTENT),
        'list_my_stickers'
    )


async def list_my_voices_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await list_my_contents_handler(
        update,
        context,
        lambda: get_all_user_described_content(update.message.from_user.id, VOICE_MESSAGE_CONTENT),
        'list_my_voices'
    )


async def list_available_stickers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await list_my_contents_handler(
        update,
        context,
        lambda: get_all_available_contents(context.user_data.get('subscribed_groups'), STICKER_CONTENT),
        'list_available_stickers'
    )


async def list_available_voices_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await list_my_contents_handler(
        update,
        context,
        lambda: get_all_available_contents(context.user_data.get('subscribed_groups'), VOICE_MESSAGE_CONTENT),
        'list_available_voices'
    )


def list_content_handlers() -> Iterable[CommandHandler]:
    yield CommandHandler('list_my_stickers', list_my_stickers_handler)
    yield CommandHandler('list_my_voices', list_my_voices_handler)

    yield CommandHandler('list_available_stickers', list_available_stickers_handler)
    yield CommandHandler('list_available_voices', list_available_voices_handler)
