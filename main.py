import asyncio
import os
import functions_framework

from src.update_handler import handle_bot_request


async def handle_async(request_json):
    await handle_bot_request(os.environ.get(f"TELEGRAM_BOT_TOKEN"), request_json)
    return {"statusCode": 200}


@functions_framework.http
def bot_assistant_handler(request):
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
