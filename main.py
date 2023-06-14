import asyncio
import os
import functions_framework

from update_handler import handle_bot_request


def get_bot_token() -> str:
    # if ':Prod' in context.invoked_function_arn:
    #     environment = ''
    # else:
    #     environment = 'DEV'

    return os.environ.get(f"TELEGRAM_BOT_TOKEN")


async def handle_async(request):
    async def get_request_data():
        return request.get_json(silent=True)

    await handle_bot_request(get_bot_token(), get_request_data)
    return {"statusCode": 200}


@functions_framework.http
def hello_http(request):
    request_json = request.get_json(silent=True)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        if str(e).startswith('There is no current event loop in thread'):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            raise

    return loop.run_until_complete(handle_async(request_json))
