import asyncio
import json
import os
import sys

from telegram import Update, Bot

from update_handler import handle_update


def get_bot_token(context) -> str:
    if ':Prod' in context.invoked_function_arn:
        environment = ''
    else:
        environment = 'DEV'

    return os.environ.get(f"{environment}_TELEGRAM_BOT_TOKEN")


async def handle_async(event, context):
    try:
        async with Bot(token=get_bot_token(context)) as bot:
            update = Update.de_json(json.loads(event['body']), bot)
            await handle_update(update)
    except Exception as e:
        print(e, file=sys.stderr)
        return {"statusCode": 500}

    return {"statusCode": 204}


def lambda_handler(event, context):
    return asyncio.get_event_loop().run_until_complete(handle_async(event, context))
