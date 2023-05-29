import sys

from telegram import Update
from telegram.error import Forbidden, BadRequest


async def handle_update(update: Update, context=None) -> None:
    if update is None or update.message is None:
        return

    if update.message.from_user is None or update.message.from_user.is_bot:
        return

    try:
        await handle_core(update)
    except Forbidden as e:
        print(f"Unauthorized: {e}", file=sys.stderr)
    except BadRequest as e:
        print(f"Bad request: {e}", file=sys.stderr)


async def handle_core(update: Update):
    await update.message.reply_text('Hello')
