import asyncio
import json
import os

from update_handler import handle_bot_request


def get_bot_token(context) -> str:
    if ':Prod' in context.invoked_function_arn:
        environment = ''
    else:
        environment = 'DEV'

    return os.environ.get(f"{environment}_TELEGRAM_BOT_TOKEN")


async def handle_async(event, context):
    async def get_request_data():
        return json.loads(event['body'])

    await handle_bot_request(get_bot_token(context), get_request_data)
    return {"statusCode": 200}


def lambda_handler(event, context):
    return asyncio.get_event_loop().run_until_complete(handle_async(event, context))
