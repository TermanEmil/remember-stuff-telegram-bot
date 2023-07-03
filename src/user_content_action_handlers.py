from typing import Iterable, List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import BaseHandler, CallbackQueryHandler, ContextTypes

from src.auxiliary.logger import logger
from src.bot_utils import extract_message
from src.user_content import delete_content_description, UserContent, STICKER_CONTENT, VOICE_MESSAGE_CONTENT, \
    find_content_by_id, user_allowed_to_touch_content, find_with_description


async def send_user_content_with_callback_actions(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        contents: List[UserContent]
) -> None:
    message = extract_message(update)

    if len(contents) == 0:
        await message.reply_text('Content has no descriptions.')
        return

    user_id = message.from_user.id
    content_id = contents[0]['content_id']
    content_file_id = contents[0]['content_file_id']
    content_type = contents[0]['type']

    buttons = []
    for content in contents:
        prefix = ''
        if user_allowed_to_touch_content(context.user_data, user_id, content):
            prefix = '❌ '

        for description in content['descriptions']:
            button = InlineKeyboardButton(text=f'{prefix}{description}', callback_data=f'{content_id}]|[{description}')
            buttons.append([button])

    keyboard = InlineKeyboardMarkup(buttons)

    try:
        if content_type == STICKER_CONTENT:
            await message.reply_sticker(sticker=content_file_id, disable_notification=True, reply_markup=keyboard)
        elif content_type == VOICE_MESSAGE_CONTENT:
            await message.reply_voice(voice=content_file_id, disable_notification=True, reply_markup=keyboard)
    except Exception as e:
        logger.critical(e, exc_info=True)
        await message.reply_text('🚨 Failed to send content.')


async def keyboard_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer()
    if len(query.data) == 0:
        return

    message = extract_message(update)
    content_id, description = query.data.split(']|[')
    content = find_with_description(content_id, description)

    if content is None:
        await message.reply_text(f'Could not find the description.')
        return

    if not user_allowed_to_touch_content(context.user_data, query.from_user.id, content):
        await message.reply_text(f'You do not have permission over this description: {description}')
        return

    deleted_element = delete_content_description(content_id=content_id, description=description)
    if not deleted_element:
        await message.reply_text(f'Failed to remove the description.')
        return

    await message.reply_text(
        f'Description <i>{description}</i> removed.',
        parse_mode='html',
        disable_notification=True
    )
    updated_content = find_content_by_id(content_id)
    await send_user_content_with_callback_actions(update, context, updated_content)


def user_content_action_handlers() -> Iterable[BaseHandler]:
    yield CallbackQueryHandler(keyboard_button_handler)
