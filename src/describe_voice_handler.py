from datetime import datetime, timezone
from typing import Iterable, List

from telegram import Update
from telegram.ext import BaseHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from src.user_content import UserContent, split_descriptions, VOICE_MESSAGE_CONTENT, save_user_content, \
    find_content_by_id
from src.user_content_action_handlers import send_user_content_with_callback_actions

SEND_VOICE, SEND_VOICE_TITLE, SEND_VOICE_DESCRIPTION = range(3)
BROADCASTING_CHAT_ID = -1001757896768


async def describe_voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Okay, now send me a voice message.')
    return SEND_VOICE


async def send_voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.voice is None:
        await update.message.reply_text('Voice message required!')
        return SEND_VOICE

    context.user_data['voice_id'] = update.message.voice.file_unique_id
    context.user_data['voice_file_id'] = update.message.voice.file_id
    context.user_data['voice_duration'] = update.message.voice.duration

    content = find_content_by_id(update.message.voice.file_unique_id, context.user_data.get('subscribed_groups'))
    await send_user_content_with_callback_actions(update, context, content)
    await update.message.reply_text('Now give this voice message a title.')
    return SEND_VOICE_TITLE


async def send_title_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text is None or len(update.message.text) == 0:
        await update.message.reply_text('A title for the voice message required.')
        return SEND_VOICE_TITLE

    context.user_data['voice_title'] = update.message.text

    await update.message.reply_text('Now add some descriptions.')
    return SEND_VOICE_DESCRIPTION


async def send_descriptions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text is None or len(update.message.text) == 0:
        await update.message.reply_text('Descriptions too short')
        return SEND_VOICE_DESCRIPTION

    descriptions = split_descriptions(update.message.text)
    max_size = 50

    if any(len(description) > max_size for description in descriptions):
        await update.message.reply_text(f'Descriptions may not exceed {max_size}.')
        return SEND_VOICE_DESCRIPTION

    user_id = update.message.from_user.id
    groups = context.user_data['broadcasting_groups']
    voice_id = context.user_data.get('voice_id')
    voice_file_id = context.user_data.get('voice_file_id')
    voice_duration = context.user_data.get('voice_duration')
    voice_title = context.user_data.get('voice_title')

    user_content = UserContent(
        user_id=user_id,
        content_id=voice_id,
        content_file_id=voice_file_id,
        descriptions=descriptions,
        groups=groups,
        title=voice_title,
        duration=voice_duration,
        type=VOICE_MESSAGE_CONTENT,
        date_created=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc)
    )
    save_user_content(user_content)

    readable_descriptions = ', '.join(descriptions)
    s = 's' if len(descriptions) > 1 else ''
    await update.message.reply_text(
        f"The voice message <i>{voice_title}</i> was saved with the following description{s}:\n"
        f"<i>{readable_descriptions}</i>\n"
        "To start again use /describe_voice",
        disable_notification=True,
        parse_mode='html'
    )

    content = find_content_by_id(voice_id, context.user_data.get('subscribed_groups'))
    await send_user_content_with_callback_actions(update, context, content)

    # Broadcast the voice message on a channel to allow the reuse of the voice_file_id between other bots.
    # Simply broadcasting a message to a channel in which these bots are added is enough to use the same file id.
    # I'm doing this is so that my uploads from my development bot are available on prod as well.
    await update.get_bot().send_voice(BROADCASTING_CHAT_ID, voice=voice_file_id, caption=voice_title)

    return ConversationHandler.END


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Cancelled')
    return ConversationHandler.END


def describe_voice_handlers() -> Iterable[BaseHandler]:
    yield ConversationHandler(
        name='describe_voice_conversation',
        entry_points=[CommandHandler("describe_voice", describe_voice_handler)],
        states={
            SEND_VOICE: [MessageHandler(filters.ALL & (~ filters.COMMAND), send_voice_handler)],
            SEND_VOICE_TITLE: [MessageHandler(filters.ALL & (~ filters.COMMAND), send_title_handler)],
            SEND_VOICE_DESCRIPTION: [MessageHandler(filters.ALL & (~ filters.COMMAND), send_descriptions_handler)]
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
        persistent=True,
        allow_reentry=True,
    )
