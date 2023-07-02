from typing import Iterable

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


GLOBAL = 'public'


async def join_public_group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if GLOBAL not in context.user_data['subscribed_groups']:
        context.user_data['subscribed_groups'].append(GLOBAL)
        await update.message.reply_text('Subscribed to global.')
    else:
        await update.message.reply_text('Already subscribed to global.')


async def leave_public_group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    await update.message.reply_text(f'You are currently subscribe to the following groups:\n{readable_groups}.')


async def list_broadcasting_groups_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    personal_group = f'user-{user_id}'
    groups = context.user_data['broadcasting_groups']
    groups = ('personal' if x == personal_group else x for x in groups)
    readable_groups = ', '.join(groups)
    await update.message.reply_text(f'You are currently broadcasting to the following groups:\n{readable_groups}.')


async def broadcast_to_public_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if GLOBAL not in context.user_data['broadcasting_groups']:
        context.user_data['broadcasting_groups'].append(GLOBAL)
        await update.message.reply_text('Broadcasting to public.')
    else:
        await update.message.reply_text('Already broadcasting to public.')


async def stop_broadcasting_to_public_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if GLOBAL in context.user_data['broadcasting_groups']:
        context.user_data['broadcasting_groups'].remove(GLOBAL)
        await update.message.reply_text('Not broadcasting to public anymore.')
    else:
        await update.message.reply_text('Already not broadcasting to public.')


async def groups_help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        '/list_subscribed_groups - See your subscribed groups\n'
        '/list_broadcasting_groups - See your broadcasting groups\n'
        '/join_public - Join public group of descriptions\n'
        '/leave_public - Stop seeing public descriptions\n'
        '/broadcast_to_public - Start broadcasting to the public\n'
        '/stop_broadcasting_to_public - Stop broadcasting to the public\n'
    )


def groups_handlers() -> Iterable[CommandHandler]:
    yield CommandHandler('groups', groups_help_handler)
    yield CommandHandler('groups_help', groups_help_handler)

    yield CommandHandler('join_public', join_public_group_handler)
    yield CommandHandler('leave_public', leave_public_group_handler)
    yield CommandHandler('list_subscribed_groups', list_subscribed_groups_handler)
    yield CommandHandler('list_broadcasting_groups', list_broadcasting_groups_handler)
    yield CommandHandler('broadcast_to_public', broadcast_to_public_handler)
    yield CommandHandler('stop_broadcasting_to_public', stop_broadcasting_to_public_handler)
