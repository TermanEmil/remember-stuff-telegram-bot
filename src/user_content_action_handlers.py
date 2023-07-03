from typing import Iterable, List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import BaseHandler, CallbackQueryHandler, ContextTypes

from src.user_content import delete_content_description, UserContent, STICKER_CONTENT, VOICE_MESSAGE_CONTENT, \
    find_content_by_id


async def send_user_content_with_callback_actions(update: Update, contents: List[UserContent]) -> None:
    if len(contents) == 0:
        await update.message.reply_text('Content has no descriptions.')
        return

    user_id = update.message.from_user.id
    content_id = contents[0]['content_id']
    content_file_id = contents[0]['content_file_id']
    content_type = contents[0]['type']

    buttons = []
    for content in contents:
        if 'public' in content['groups']:
            prefix = '🟢 '
        elif f'user-{user_id}' in content['groups']:
            prefix = '🟡 '
        else:
            prefix = ''

        for description in content['descriptions']:
            button = InlineKeyboardButton(text=f'{prefix}{description}', callback_data=f'{content_id}]|[{description}')
            buttons.append([button])

    keyboard = InlineKeyboardMarkup(buttons)

    if content_type == STICKER_CONTENT:
        await update.message.reply_sticker(sticker=content_file_id, disable_notification=True, reply_markup=keyboard)
    elif content_type == VOICE_MESSAGE_CONTENT:
        await update.message.reply_voice(voice=content_file_id, disable_notification=True, reply_markup=keyboard)


async def keyboard_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer()

    if len(query.data) == 0:
        return

    content_id, description = query.data.split(']|[')
    # TODO: Display which descriptions are accessible
    deleted_element = delete_content_description(
        user_id=update.callback_query.from_user.id,
        content_id=content_id,
        description=description
    )

    if deleted_element:
        message = update.message if update.message else update.callback_query.message
        await message.reply_text(
            f'Description <i>{description}</i> removed.',
            parse_mode='html',
            disable_notification=True
        )
        updated_content = find_content_by_id(content_id)
        await send_user_content_with_callback_actions(update, updated_content)
    else:
        await update.callback_query.message.reply_text(
            f'Could not find the sticker with the following description: {description}'
        )


def user_content_action_handlers() -> Iterable[BaseHandler]:
    yield CallbackQueryHandler(keyboard_button_handler)
