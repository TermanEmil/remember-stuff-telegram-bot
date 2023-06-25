from typing import Iterable

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, Application, \
    CallbackQueryHandler

from src.user_content import UserContent, save_user_content, get_all_sticker_descriptions, split_descriptions, \
    STICKER_CONTENT, delete_content_description


async def describe_sticker_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Okay, now send me some stickers!')
    return SEND_STICKERS


async def send_stickers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.sticker:
        await update.message.reply_text('Sticker required!')
        return SEND_STICKERS

    sticker_id = update.message.sticker.file_unique_id
    sticker_file_id = update.message.sticker.file_id
    context.user_data['sticker_id'] = sticker_id
    context.user_data['sticker_file_id'] = sticker_file_id
    await update.message.reply_text(f"Now add some description")

    return SEND_DESCRIPTION


async def _send_sticker_with_descriptions(update: Update, sticker_id: str, sticker_file_id: str) -> None:
    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message

    all_descriptions = get_all_sticker_descriptions(sticker_id)
    buttons = map(lambda x: [InlineKeyboardButton(text=x, callback_data=f'{sticker_id}]|[{x}')], all_descriptions)

    keyboard = InlineKeyboardMarkup(list(buttons))

    await message.reply_sticker(
        sticker=sticker_file_id,
        disable_notification=True,
        reply_markup=keyboard
    )


async def send_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sticker_id = context.user_data.get('sticker_id', None)
    sticker_file_id = context.user_data.get('sticker_file_id', None)

    if sticker_id is None or sticker_file_id is None:
        await update.message.reply_text("Failed to retrieve state", disable_notification=True)
        return ConversationHandler.END

    user_id = update.message.from_user.id
    descriptions = split_descriptions(update.message.text)
    groups = [f'user-{user_id}']

    user_content = UserContent(
        user_id=user_id,
        content_id=sticker_id,
        content_file_id=sticker_file_id,
        descriptions=descriptions,
        groups=groups,
        type=STICKER_CONTENT
    )
    save_user_content(user_content)

    await update.message.reply_text(
        f"The sticker was saved with the following description: {descriptions}\n" +
        "To start again use /describe_sticker",
        disable_notification=True
    )

    await _send_sticker_with_descriptions(update, sticker_id, sticker_file_id)
    return ConversationHandler.END


async def keyboard_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer()

    if len(query.data) == 0:
        return

    sticker_id, description = query.data.split(']|[')
    deleted_element = delete_content_description(
        user_id=update.callback_query.from_user.id,
        content_id=sticker_id,
        description=description
    )

    if deleted_element:
        await _send_sticker_with_descriptions(update, sticker_id, deleted_element['content_file_id'])
    else:
        await update.callback_query.message.reply_text(
            f'Could not find the sticker with the following description: {description}'
        )


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Cancelled')
    return ConversationHandler.END


SEND_STICKERS, SEND_DESCRIPTION = range(2)


def describe_sticker_conversation_handlers() -> Iterable[ConversationHandler]:
    yield ConversationHandler(
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

    yield CallbackQueryHandler(keyboard_button_handler)
