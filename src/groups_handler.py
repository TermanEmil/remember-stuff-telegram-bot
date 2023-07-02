from typing import Iterable

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


GLOBAL = 'public'


async def join_global_group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if GLOBAL not in context.user_data['subscribed_groups']:
        context.user_data['subscribed_groups'].append(GLOBAL)
        await update.message.reply_text('Subscribed to global.')
    else:
        await update.message.reply_text('Already subscribed to global.')


async def leave_global_group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if GLOBAL in context.user_data['subscribed_groups']:
        context.user_data['subscribed_groups'].remove(GLOBAL)
        await update.message.reply_text('Unsubscribed from global.')
    else:
        await update.message.reply_text('Already unsubscribed from global.')


async def list_subscribed_groups_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    personal_group = f'user-{user_id}'
    groups = context.user_data['subscribed_groups']
    groups = ('personal' if x == personal_group else x for x in groups)
    readable_groups = ', '.join(groups)
    await update.message.reply_text(f'You are currently subscribe to the following groups: {readable_groups}.')


def groups_handlers() -> Iterable[CommandHandler]:
    yield CommandHandler('join_global', join_global_group_handler)
    yield CommandHandler('leave_global', leave_global_group_handler)
    yield CommandHandler('list_subscribed_groups', list_subscribed_groups_handler)
