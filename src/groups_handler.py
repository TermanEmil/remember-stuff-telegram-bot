from typing import Iterable

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


async def join_global_group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'global' not in context.user_data['subscribed_groups']:
        context.user_data['subscribed_groups'].append('global')
        await update.message.reply_text('Subscribed to global.')
    else:
        await update.message.reply_text('Already subscribed to global.')


async def leave_global_group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'global' in context.user_data['subscribed_groups']:
        context.user_data['subscribed_groups'].remove('global')
        await update.message.reply_text('Unsubscribed from global.')
    else:
        await update.message.reply_text('Already unsubscribed from global.')


def groups_handlers() -> Iterable[CommandHandler]:
    yield CommandHandler('join_global', join_global_group_handler)
    yield CommandHandler('leave_global', join_global_group_handler)
