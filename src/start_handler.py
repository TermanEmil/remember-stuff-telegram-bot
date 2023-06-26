from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = '\n'.join([
        f'Hi. I will help you find stickers.',
        f'You can use the /describe_sticker command to save some hand-picked stickers.',
        f'Then you can use me from any chat by typing:',
        f'@{update.get_bot().username} cat'
    ])

    try_it_out_button = InlineKeyboardButton(text='Try it out!', switch_inline_query_current_chat='cat')
    keyboard = InlineKeyboardMarkup([[try_it_out_button]])
    await update.message.reply_text(text, reply_markup=keyboard)
