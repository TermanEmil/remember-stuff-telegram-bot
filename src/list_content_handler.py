import math
import re
from typing import Iterable

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes

from src.user_content import get_all_user_described_stickers, UserContent


async def _send_sticker_with_descriptions(update: Update, sticker: UserContent) -> None:
    sticker_id = sticker['content_id']
    sticker_file_id = sticker['content_file_id']
    all_descriptions = sticker['descriptions']

    buttons = map(lambda description: [
        InlineKeyboardButton(text=f'❌ {description}', callback_data=f'{sticker_id}]|[{description}')
    ], all_descriptions)

    keyboard = InlineKeyboardMarkup(list(buttons))

    await update.message.reply_sticker(
        sticker=sticker_file_id,
        disable_notification=True,
        reply_markup=keyboard
    )


async def list_my_stickers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = re.sub(r'^/\w+', '', update.message.text).strip()
    match = re.search(r'page (\d+)', text, re.IGNORECASE)
    if match:
        page = int(match.group(1))
    else:
        page = 1

    page_size = 20
    user_id = update.message.from_user.id
    all_stickers = get_all_user_described_stickers(user_id)
    paginated_stickers = all_stickers[(page - 1) * page_size:page * page_size]
    total_pages = int(math.ceil(len(all_stickers) / page_size))
    has_next = (page + 1) * page_size <= len(all_stickers)

    for sticker in paginated_stickers:
        await _send_sticker_with_descriptions(update, sticker)

    if has_next:
        buttons = [[f'/list_my_stickers page {page + 1}']]
        keyboard = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f'Press the button to view the next ones.\nCurrently at {page}/{total_pages}.',
            reply_markup=keyboard
        )


def list_content_handlers() -> Iterable[CommandHandler]:
    yield CommandHandler('list_my_stickers', list_my_stickers_handler)
