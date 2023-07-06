from telegram import Update, Message


def extract_message(update: Update) -> Message:
    if update.message:
        return update.message

    if update.callback_query:
        return update.callback_query.message


def stringify(update: Update) -> str:
    if update.inline_query:
        update_type = 'inline_query'
        text = update.inline_query.query
        user_id = update.inline_query.from_user.id
    elif update.message:
        update_type = 'message'
        text = update.message.text
        user_id = update.message.from_user.id
    elif update.callback_query:
        update_type = 'callback_query'
        text = update.callback_query.message.text
        user_id = update.callback_query.from_user.id
    else:
        update_type = '<UnknownType>'
        text = '<Unable to find text>'
        user_id = -1

    return f'{update_type}: user_id-{user_id}: text: {text}'
