from telegram import Update, Message


def extract_message(update: Update) -> Message:
    if update.message:
        return update.message

    if update.callback_query:
        return update.callback_query.message

