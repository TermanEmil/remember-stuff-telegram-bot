from typing import Callable, Awaitable, Dict, Any

from telegram import Update
from telegram.ext import Application, CommandHandler

JSONDict = Dict[str, Any]


async def start_handler(update: Update, context) -> None:
    await update.message.reply_text('Hello')


async def handle_bot_request(bot_token: str, get_request_data: Callable[[], Awaitable[JSONDict]]):
    async with Application.builder().token(bot_token).updater(None).build() as application:
        application.add_handler(CommandHandler("start", start_handler))
        update = Update.de_json(data=await get_request_data(), bot=application.bot)
        await application.process_update(update)


async def setup_webhook(bot_token: str, url: str):
    application = Application.builder().token(bot_token).build()
    await application.bot.set_webhook(url=url)
