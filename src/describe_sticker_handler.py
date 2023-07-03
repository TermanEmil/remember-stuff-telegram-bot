import re
from datetime import datetime, timezone
from typing import Iterable

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, BaseHandler

from src.user_content import UserContent, save_user_content, split_descriptions, \
    STICKER_CONTENT, find_content_by_id
from src.user_content_action_handlers import send_user_content_with_callback_actions

SEND_STICKERS, SEND_DESCRIPTION = range(2)

EXAMPLE_USAGE = 'Example: <i>Lorem Ipsum, Foo, Bar</i>'


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

    content = find_content_by_id(sticker_id)
    await send_user_content_with_callback_actions(update, context, content)
    await update.message.reply_text("Now add some descriptions.")

    return SEND_DESCRIPTION


async def _send_description_handler_with_params(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        sticker_id: str,
        sticker_file_id: str,
        description: str
):
    user_id = update.message.from_user.id
    groups = context.user_data['broadcasting_groups']

    descriptions = split_descriptions(description)
    max_size = 50

    if any(len(description) > max_size for description in descriptions):
        await update.message.reply_text(f'Descriptions may not exceed {max_size}.')
        return False

    user_content = UserContent(
        user_id=user_id,
        content_id=sticker_id,
        content_file_id=sticker_file_id,
        descriptions=descriptions,
        groups=groups,
        type=STICKER_CONTENT,
        title='sticker',
        duration=None,
        date_created=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc)
    )
    save_user_content(user_content)

    readable_descriptions = ', '.join(descriptions)
    s = 's' if len(descriptions) > 1 else ''
    await update.message.reply_text(
        f"The sticker was saved with the following description{s}:\n"
        f"<i>{readable_descriptions}</i>\n"
        "To start again use /describe_sticker",
        disable_notification=True,
        parse_mode='html'
    )

    new_content = find_content_by_id(sticker_id)
    await send_user_content_with_callback_actions(update, context, new_content)
    return True


async def send_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sticker_id = context.user_data.get('sticker_id', None)
    sticker_file_id = context.user_data.get('sticker_file_id', None)
    description = update.message.text

    if sticker_id is None or sticker_file_id is None:
        await update.message.reply_text("Failed to retrieve state. Cancelling.", disable_notification=True)
        return ConversationHandler.END

    if not description or len(description) == 0:
        await update.message.reply_text(
            f"Description required!\n"
            f"{EXAMPLE_USAGE}",
            disable_notification=True,
            parse_mode='html'
        )
        return SEND_DESCRIPTION

    if await _send_description_handler_with_params(update, context, sticker_id, sticker_file_id, description):
        return ConversationHandler.END
    else:
        return SEND_DESCRIPTION


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Cancelled')
    return ConversationHandler.END


async def describe_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
        await update.message.reply_text(
            'The command must be ran either as a reply to a sticker or without any text.'
        )
        return

    sticker_id = update.message.reply_to_message.sticker.file_unique_id
    sticker_file_id = update.message.reply_to_message.sticker.file_id
    text = re.sub(r'^/\w+', '', update.message.text)

    await _send_description_handler_with_params(update, context, sticker_id, sticker_file_id, text)


def describe_sticker_conversation_handlers() -> Iterable[BaseHandler]:
    non_empty_text = filters.TEXT & filters.Regex(r"\s+")
    yield CommandHandler('describe_sticker', describe_sticker, filters=non_empty_text)

    yield ConversationHandler(
        name='describe_sticker_conversation',
        entry_points=[CommandHandler("describe_sticker", describe_sticker_handler)],
        states={
            SEND_STICKERS: [MessageHandler(filters.ALL & (~ filters.COMMAND), send_stickers_handler)],
            SEND_DESCRIPTION: [MessageHandler(filters.ALL & (~ filters.COMMAND), send_description_handler)]
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
        persistent=True,
        allow_reentry=True,
    )
