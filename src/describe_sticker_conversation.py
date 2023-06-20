from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

from src.user_content import UserContent, save_user_content, get_all_sticker_descriptions


async def describe_sticker_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Okay, now send me some stickers!')
    return SEND_STICKERS


async def send_stickers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.sticker:
        await update.message.reply_text('Sticker required!')
        return SEND_STICKERS

    sticker_id = update.message.sticker.file_id
    context.user_data['conversation_sticker_id'] = sticker_id
    await update.message.reply_text(f"Now add some description")

    return SEND_DESCRIPTION


async def send_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    sticker_id = context.user_data['conversation_sticker_id']
    description = update.message.text

    user_content = UserContent(
        user_id=user_id,
        content_id=sticker_id,
        description=description,
        groups=[f'user-{user_id}']
    )
    save_user_content(user_content)

    await update.message.reply_text(
        f"The sticker was saved with the following description: {description}\n" +
        "To start again use /describe_sticker",
        disable_notification=True
    )

    descriptions = get_all_sticker_descriptions(sticker_id)
    buttons = map(lambda x: InlineKeyboardButton(text=x, callback_data=f'{user_id}_{x}'), descriptions)
    keyboard = InlineKeyboardMarkup([list(buttons)])

    await update.message.reply_sticker(
        sticker=sticker_id,
        disable_notification=True,
        reply_markup=keyboard
    )
    return ConversationHandler.END


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Cancelled')
    return ConversationHandler.END


SEND_STICKERS, SEND_DESCRIPTION = range(2)


def describe_sticker_conversation() -> ConversationHandler:
    return ConversationHandler(
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
